# 1. Stop the running app (Ctrl+C in terminal)

# 2. Verify CSV is readable
python -c "import pandas as pd; df = pd.read_csv('ikeja_security_social_media.csv'); print(f'CSV has {len(df)} rows')"

# 3. Test CSV loader directly
python -c "from app.core.csv_data_loader import CSVDataLoader; loader = CSVDataLoader('ikeja_security_social_media.csv'); print(f'Loaded {len(loader.get_sample_data(10))} items')"

# 4. Restart app with verbose logging
python -m app.main