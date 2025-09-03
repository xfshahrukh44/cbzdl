# cbzdl

A Python project for downloading and managing CBZ files.

## Features

- Download CBZ files from supported sources
- Organize and manage your comic book library

## Requirements

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/cbzdl.git
   cd cbzdl
   ```

2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```sh
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```sh
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   If you don't have a `requirements.txt`, install manually:
   ```sh
   pip install requests pillow playwright
   python -m playwright install
   ```

## Usage

Run the main script:

```sh
python weebcentral.py
```

You will be prompted to enter the page URL of the chapter you want to download.

## Output

- CBZ files will be saved in the `out/<series title>/` directory.

## Notes

- The script uses [Playwright](https://playwright.dev/python/) for browser automation. The first run may download browser binaries.
- Make sure you have a stable internet connection for downloading images and browser automation.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)