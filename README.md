# Trust Dashboard v5

### Improvements:
- FSM % fixed using PercentageFSM column
- Removed average FSM summary
- Removed “Type” field
- Added address + Head's name
- Filters rebuilt and now work properly
- Fixed school comparison multiselect
- Embedded Ofsted search page in iframe

## Run:
1. Add `National datasheeet.csv` to this folder
2. Install dependencies and run:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```