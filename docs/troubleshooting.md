# Troubleshooting & Frequently Encountered Issues

This guide resolves common runtime, configuration, and environment issues.

---

## 1. Python Environment & Dependency Issues

### Issue: `ModuleNotFoundError: No module named 'src'`
**Cause:** Python cannot resolve the project root if scripts are executed outside editable install mode.  
**Resolution:**  
Install the repository in editable mode:
```bash
pip install -e .
```
All CLI scripts also include `sys.path.insert(0, str(Path(__file__).parent.parent))` at the entrypoint for standalone execution.

---

### Issue: `RuntimeWarning: opencv-contrib-python not available. Falling back to ManualBRIEF`
**Cause:** Standard `opencv-python` does not include `cv2.xfeatures2d.BriefDescriptorExtractor`.  
**Resolution:**  
This is normal behavior and handled gracefully. The pipeline contains an in-tree `ManualBRIEF` implementation (genuine Gaussian-sampled 256-bit binary tests) that matches OpenCV's BRIEF specification exactly and labels results appropriately in output tables. If `opencv-contrib-python` is desired:
```bash
pip install opencv-contrib-python
```

---

## 2. Dataset Loading & File Formatting

### Issue: `yaml.scanner.ScannerError: mapping values are not allowed here`
**Cause:** UTF-8 files saved with a Byte Order Mark (`\xef\xbb\xbf`) can break YAML parsers.  
**Resolution:**  
The project loaders (`experiments/runner.py` and `experiments/benchmark.py`) employ `encoding="utf-8-sig"` which automatically strips BOM headers during parsing.

### Issue: Trajectory file missing during evaluation
**Cause:** The benchmark or VO pipeline has not been executed yet for that specific configuration.  
**Resolution:**  
Run the experiment before evaluating:
```bash
python scripts/run_vo.py --config configs/experiments/faster_orb.yaml --dataset configs/datasets/icl_nuim.yaml
```

---

## 3. Visualization & Headless Server Environments

### Issue: `_tkinter.TclError: no display name and no $DISPLAY environment variable`
**Cause:** Matplotlib attempting to open an interactive GUI window on headless servers or WSL.  
**Resolution:**  
All visualization modules explicitly declare:
```python
import matplotlib
matplotlib.use("Agg")  # Non-interactive raster backend
```
This guarantees headless figure rendering and direct file saving without X11 server dependencies.

