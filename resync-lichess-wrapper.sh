cd lichess-bot
git pull
cd ..
cp src/strategies.py src/strategies-bkp.py
cp -r lichess-bot/* src
mv src/strategies-bkp.py src/strategies.py
rm src/LICENSE
rm -r src/test_bot
python3 -m pip install -r requirements.txt