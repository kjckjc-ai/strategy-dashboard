# Trust Explorer Streamlit App

Explore schools within any Multi-Academy Trust using fuzzy search and interactive filtering. This dashboard allows users to:

- Search for a trust using approximate name matching
- View a table of all schools within the trust
- Filter by phase of education
- View a geographic map of school locations (if coordinates available)

## Usage
Place `National datasheeet.csv` in the root folder, then run:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```