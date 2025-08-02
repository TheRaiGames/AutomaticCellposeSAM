#!/usr/bin/env python3
"""
Automated Cellpose Segmentation Script
Batch processes .tif images using Cellpose 4.0.4 with CPSAM model
Compatible with Python 3.13.5
"""

import os
import sys
import glob
import argparse
import logging
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

def check_python_version():
    """Check if the Python version is compatible"""
    recommended_version = (3, 13, 5)
    minimum_version = (3, 8, 0)
    current_version = sys.version_info[:3]
    
    if current_version >= recommended_version:
        print(f"✓ Python version optimal: {'.'.join(map(str, current_version))}")
        return True
    elif current_version >= minimum_version:
        print(f"⚠ Python version acceptable: {'.'.join(map(str, current_version))} (recommended: {'.'.join(map(str, recommended_version))})")
        return True
    else:
        print(f"✗ Python version too old: {'.'.join(map(str, current_version))} (minimum: {'.'.join(map(str, minimum_version))})")
        return False

def check_cellpose_installation():
    """Check if Cellpose is installed and accessible"""
    try:
        import cellpose
        try:
            version = cellpose.__version__
            print(f"Cellpose version: {version}")
            if not version.startswith("4.0"):
                print(f"Warning: Cellpose 4.0.x recommended, but {version} is installed")
        except AttributeError:
            print("Cellpose is installed (version detection unavailable)")
        return True
    except ImportError:
        print("Error: Cellpose not found. Please install cellpose")
        return False

def check_torch_cuda():
    """Check if PyTorch with CUDA is available"""
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        if torch.cuda.is_available():
            print("CUDA is available and working")
            return True
        else:
            print("Warning: CUDA not available, will use CPU (slower)")
            return False
    except ImportError:
        print("Error: PyTorch not found")
        return False

def select_folder(title="Select Folder"):
    """Open a folder selection dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring to front
    
    folder_path = filedialog.askdirectory(title=title)
    root.destroy()
    
    return folder_path

def get_tif_files(input_folder):
    """Get all .tif and .tiff files from the input folder"""
    tif_patterns = ['*.tif', '*.tiff', '*.TIF', '*.TIFF']
    tif_files = []
    
    for pattern in tif_patterns:
        tif_files.extend(glob.glob(os.path.join(input_folder, pattern)))
    
    # Remove duplicates and sort
    return sorted(list(set(tif_files)))

def run_cellpose_batch(input_folder, output_folder, model='cpsam', diameter=None, channels=[0,0]):
    """
    Run Cellpose batch processing on all .tif files in input folder
    
    Args:
        input_folder (str): Path to folder containing .tif images
        output_folder (str): Path to folder for output files
        model (str): Cellpose model to use (default: 'cpsam')
        diameter (float): Cell diameter (0 for auto-detection)
        channels (list): Channel configuration [cytoplasm, nucleus]
    """
    
    # Get all .tif files
    tif_files = get_tif_files(input_folder)
    
    if not tif_files:
        print(f"No .tif files found in {input_folder}")
        return False
    
    print(f"Found {len(tif_files)} .tif files to process")
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Setup logging
    log_file = os.path.join(output_folder, 'batch_processing.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting batch processing of {len(tif_files)} files")
    logger.info(f"Input folder: {input_folder}")
    logger.info(f"Output folder: {output_folder}")
    logger.info(f"Model: {model}")
    
    success_count = 0
    failed_files = []
    
    try:
        from cellpose import models, io
        
        # Initialize model
        logger.info(f"Loading Cellpose model: {model}")
        model_instance = models.CellposeModel(gpu=True, pretrained_model=model)
        
        for i, tif_file in enumerate(tif_files, 1):
            try:
                logger.info(f"Processing file {i}/{len(tif_files)}: {os.path.basename(tif_file)}")
                
                # Read image
                img = io.imread(tif_file)
                logger.info(f"Image shape: {img.shape}")
                logger.info(f"Image dtype: {img.dtype}")
                logger.info(f"Image min/max: {img.min()}/{img.max()}")
                
                # Run segmentation (channels parameter deprecated in Cellpose-SAM 4.0.6+)
                logger.info(f"Running segmentation with diameter={diameter}")
                try:
                    result = model_instance.eval(
                        img, 
                        diameter=diameter,
                        flow_threshold=0.4,
                        cellprob_threshold=0.0
                    )
                    # Handle different return formats between Cellpose versions
                    if len(result) == 4:
                        masks, flows, styles, diams = result
                    elif len(result) == 3:
                        masks, flows, styles = result
                        diams = None
                    else:
                        logger.error(f"Unexpected return format: {len(result)} values")
                        raise ValueError(f"Unexpected eval return format")
                        
                    # Count cells (unique labels excluding 0)
                    if isinstance(masks, list):
                        cell_count = len(masks) if masks else 0
                    else:
                        import numpy as np
                        cell_count = len(np.unique(masks)) - 1 if 0 in np.unique(masks) else len(np.unique(masks))
                    logger.info(f"Segmentation completed - found {cell_count} cells")
                    
                except Exception as eval_error:
                    logger.error(f"Error during model.eval: {eval_error}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    raise eval_error
                
                # Generate output filename
                base_name = os.path.splitext(os.path.basename(tif_file))[0]
                
                # Save results with proper data type handling
                import numpy as np
                base_name = os.path.splitext(os.path.basename(tif_file))[0]
                
                # Preprocess masks to ensure compatibility with save_masks
                processed_masks = masks
                if isinstance(masks, np.ndarray):
                    # Check if mask values exceed uint16 range and need remapping
                    if masks.max() > 65535:
                        logger.info(f"Masks contain values > 65535 (max: {masks.max()}), remapping to sequential labels")
                        # Remap to sequential labels starting from 1
                        unique_labels = np.unique(masks)
                        unique_labels = unique_labels[unique_labels > 0]  # Remove background (0)
                        processed_masks = np.zeros_like(masks, dtype=np.uint16)
                        for i, label in enumerate(unique_labels):
                            processed_masks[masks == label] = i + 1
                        logger.info(f"Remapped {len(unique_labels)} labels to range 1-{len(unique_labels)}")
                    elif masks.max() > 255:
                        # Convert to uint16 if values exceed uint8 but fit in uint16
                        processed_masks = masks.astype(np.uint16)
                    else:
                        # Keep as original type if values fit in uint8
                        processed_masks = masks
                
                try:
                    # Try the standard save_masks function with preprocessed masks
                    io.save_masks(
                        img, 
                        processed_masks, 
                        flows, 
                        tif_file, 
                        savedir=output_folder,
                        save_flows=True,
                        save_outlines=True
                    )
                    logger.info(f"Successfully saved all files using standard method")
                    
                except Exception as save_error:
                    logger.warning(f"Error saving with save_masks: {save_error}")
                    logger.info("Using alternative save method for flows and masks...")
                    
                    # Alternative comprehensive save approach
                    from PIL import Image
                    import tifffile
                    
                    # 1. Save masks with proper data type
                    if isinstance(processed_masks, np.ndarray):
                        mask_file = os.path.join(output_folder, f"{base_name}_masks.tif")
                        masks_save = processed_masks.astype(np.uint16) if processed_masks.max() < 65535 else processed_masks.astype(np.uint32)
                        tifffile.imwrite(mask_file, masks_save)
                        logger.info(f"Saved masks to {mask_file}")
                    
                    # 2. Save flows data if available
                    if flows and len(flows) > 0:
                        try:
                            # Save flow fields (flows[1] contains the actual flow vectors)
                            if len(flows) > 1 and flows[1] is not None:
                                flows_file = os.path.join(output_folder, f"{base_name}_flows.tif")
                                flow_data = flows[1].astype(np.float32)
                                tifffile.imwrite(flows_file, flow_data)
                                logger.info(f"Saved flows to {flows_file}")
                            
                            # Save cell probability (flows[2] contains cellprob)
                            if len(flows) > 2 and flows[2] is not None:
                                cellprob_file = os.path.join(output_folder, f"{base_name}_cellprob.tif")
                                cellprob_data = flows[2].astype(np.float32)
                                tifffile.imwrite(cellprob_file, cellprob_data)
                                logger.info(f"Saved cell probability to {cellprob_file}")
                                
                            # Save flow visualization (flows[0] contains RGB flow)
                            if len(flows) > 0 and flows[0] is not None:
                                flow_rgb_file = os.path.join(output_folder, f"{base_name}_flows_rgb.png")
                                flow_rgb = flows[0].astype(np.uint8)
                                Image.fromarray(flow_rgb).save(flow_rgb_file)
                                logger.info(f"Saved flow RGB to {flow_rgb_file}")
                                
                        except Exception as flow_error:
                            logger.warning(f"Error saving flows: {flow_error}")
                    
                    # 3. Save basic outlines if possible
                    try:
                        from cellpose import utils
                        outlines = utils.masks_to_outlines(processed_masks)
                        outline_file = os.path.join(output_folder, f"{base_name}_outlines.tif")
                        tifffile.imwrite(outline_file, outlines.astype(np.uint8))
                        logger.info(f"Saved outlines to {outline_file}")
                    except Exception as outline_error:
                        logger.warning(f"Error saving outlines: {outline_error}")
                
                logger.info(f"Successfully processed {os.path.basename(tif_file)} - {cell_count} cells found")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process {os.path.basename(tif_file)}: {str(e)}")
                failed_files.append(tif_file)
                continue
    
    except Exception as e:
        logger.error(f"Error initializing Cellpose: {str(e)}")
        return False
    
    # Summary
    logger.info(f"Batch processing completed!")
    logger.info(f"Successfully processed: {success_count}/{len(tif_files)} files")
    
    if failed_files:
        logger.info(f"Failed files: {len(failed_files)}")
        for failed_file in failed_files:
            logger.info(f"  - {os.path.basename(failed_file)}")
    
    return success_count > 0

def main():
    """Main function for command line interface"""
    parser = argparse.ArgumentParser(description='Automated Cellpose Batch Segmentation')
    parser.add_argument('--input', '-i', help='Input folder containing .tif images')
    parser.add_argument('--output', '-o', help='Output folder for results')
    parser.add_argument('--model', '-m', default='cpsam', help='Cellpose model (default: cpsam)')
    parser.add_argument('--diameter', '-d', type=float, default=None, help='Cell diameter (None for auto)')
    parser.add_argument('--chan1', type=int, default=0, help='Cytoplasm channel (default: 0)')
    parser.add_argument('--chan2', type=int, default=0, help='Nucleus channel (default: 0)')
    parser.add_argument('--gui', action='store_true', help='Use GUI for folder selection')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Automated Cellpose Segmentation")
    print("=" * 60)
    
    # Check system requirements (continue with warnings)
    check_python_version()  # Just warn, don't exit
    
    if not check_cellpose_installation():
        print("Warning: Cellpose check failed, but attempting to continue...")
        # Don't exit - try to continue
    
    check_torch_cuda()
    
    # Get input and output folders
    if args.gui or not args.input:
        print("\nSelect input folder containing .tif images...")
        input_folder = select_folder("Select Input Folder (containing .tif images)")
        if not input_folder:
            print("No input folder selected. Exiting.")
            sys.exit(1)
    else:
        input_folder = args.input
    
    if args.gui or not args.output:
        print("\nSelect output folder for results...")
        output_folder = select_folder("Select Output Folder (for results)")
        if not output_folder:
            print("No output folder selected. Exiting.")
            sys.exit(1)
    else:
        output_folder = args.output
    
    # Validate folders
    if not os.path.exists(input_folder):
        print(f"Error: Input folder does not exist: {input_folder}")
        sys.exit(1)
    
    print(f"\nInput folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Model: {args.model}")
    print(f"Channels: [{args.chan1}, {args.chan2}]")
    
    # Confirm before processing
    if args.gui:
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(
            "Confirm Processing", 
            f"Process all .tif files in:\n{input_folder}\n\nOutput to:\n{output_folder}\n\nProceed?"
        )
        root.destroy()
        if not result:
            print("Processing cancelled.")
            sys.exit(0)
    
    # Run batch processing
    print("\nStarting batch processing...")
    success = run_cellpose_batch(
        input_folder=input_folder,
        output_folder=output_folder,
        model=args.model,
        diameter=args.diameter,
        channels=[args.chan1, args.chan2]
    )
    
    if success:
        print("\nBatch processing completed successfully!")
    else:
        print("\nBatch processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()