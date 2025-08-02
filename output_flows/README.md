# Output Directory

This directory contains example output files from Cellpose segmentation processing.

## Generated File Types

When you process images, the following files are created for each input image:

### Core Output Files
- `*_masks.tif` - Segmentation masks (2-4MB)
- `*_flows.tif` - Flow field data (8-12MB)  
- `*_cellprob.tif` - Cell probability maps (4-6MB)
- `*_outlines.tif` - Cell boundary outlines (1-2MB)

### Visualization Files (Optional)
- `*_flows_rgb.png` - Flow field visualizations
- `*_masks.png` - Colored mask overlays

### Logs
- `batch_processing.log` - Processing logs and statistics

## Note
The actual output files are not included in the repository to keep the download size manageable. These will be generated when you run the segmentation tools on your own images.