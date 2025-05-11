#  INaturalist Web Scraper

A multithreaded web scraper built with **Python** and **Selenium** to extract plant observation images and metadata from [INaturalist.org](https://www.inaturalist.org/). This tool was created as part of a machine learning data preparation pipeline.

---

Features

-  Scrapes high-quality research-grade plant images from INaturalist
-  Collects metadata: uploader name, upload date, and observation location
-  Organizes images into folders by species and stores metadata in CSV files
-  Uses **multithreading** to accelerate the scraping process
-  Supports dynamic content loading via Selenium automation

---

Technologies Used

- Python 3
- Selenium
- Requests
- Pillow (PIL)
- CSV
- Threading

---

How to Use

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yourusername/inaturalist-scraper.git
   cd inaturalist-scraper
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Update the paths** in the script:
   - `PATH`: your ChromeDriver path
   - `csv_directory`: where to save CSVs
   - `photo_path`: where to save images
   - `csv_file_paths`: folder containing CSVs of plant names

4. **Add plant name CSV files** and update the filenames in the script (`file1`, `file2`, `file3`).

5. **Run the script**  
   ```bash
   python scraper.py
   ```

---

Output

- Folders per species with downloaded `.jpg` images
- Metadata CSV with columns:  
  `Thumbnail | URL | Uploader | Date | Location`

---

Legal Note

This tool respects the INaturalist Terms of Service. It includes rate limiting and is intended for academic/research purposes only. Please seek explicit permission if scraping at scale.

---

Author

Mohamad Al Natour  
[LinkedIn](https://www.linkedin.com/in/muhammad-natour-777a99325/) | [Email](mailto:mhmdnatour06@gmail.com)
