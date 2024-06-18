### Installation Instructions

1. Create a virtual environment:

   ```sh
   python -m venv venv
   ```

2. Activate the virtual environment:

   - On Windows:

     ```sh
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```sh
     source venv/bin/activate
     ```

3. Install the requirements:

   ```sh
   pip install -r requirements.txt
   ```

4. Download the Spacy language model:

   ```sh
   python -m spacy download en_core_web_sm
   ```
