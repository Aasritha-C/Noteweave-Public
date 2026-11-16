# Noteweave Public Demo

Run the browser extension, two-hop location queries and manual notes from a
single download. The public demo includes its own rule-based text extraction
and SQLite storage. It uses Python's standard library and runs entirely on the
presentation computer.

## Run from the ZIP

1. Install Python 3.10 or later if needed, then extract the whole ZIP.
2. Open a terminal in the extracted folder and run:

   Windows:

   ```powershell
   py -3 run_demo.py
   ```

   macOS or Linux:

   ```sh
   python3 run_demo.py
   ```

3. Leave the terminal open and visit [the demo](http://127.0.0.1:8000/).
   If port 8000 is in use, close the process using that port before starting.

## Show the implementation

- Enter **Where is Demo Notebook?** and click **Ask Question**. The demo shows
  **Demo Notebook → Demo Bag → Demo Lab** and both stored triplets.
- Under **Capture text**, enter **The pencil is in the drawer. The drawer is in
  the desk.** Click **Capture Text** and ask **Where is the pencil?**
- Open **Manual notes**, save a note, then reload the page and reopen the panel.
  The note is saved in the local database under `data/`.

## Optional browser extension

1. Open `chrome://extensions` in Chrome or `edge://extensions` in Edge.
2. Enable **Developer mode**, select **Load unpacked**, and choose the
   extracted `extension` folder.
3. Select a supported sentence on a normal web page and choose
   **Send to Noteweave** from the context menu. Use the popup to look up the
   entity, ask a location question, or save a manual note.

The public demo recognizes simple sentence patterns such as **X is in Y**,
**X is located in Y**, **X holds Y**, and **X contains Y**. It answers location
questions using up to two stored location relationships. The standalone build
uses a separate public demo backend and has no LLM dependency.
