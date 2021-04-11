# RuPauls Drag Race: May the best woman win!

Goal: Perform sentiment analysis on r/rupaulsdragrace comments, specifically from UNTUCKED series. 

User can select a season, and have the respective comments for each episode along with the predicted sentiment. The model in use here is one I built found here https://ai.stanford.edu/~amaas/data/sentiment/ I saved it to classification_model.pkl. 

Tools in use:
PRAW: reddit crawler
requests: Scrape queen names
Dash: Application


How to get script to run:
- Fill in reddit_credentials with your credentials
- Install the requirements.txt file
- Run script


To run script:
`bash`
python main.py
`bash`


