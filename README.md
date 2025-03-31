# Youtube Notification System
A system to notify myself when one of my favourite channels is publishing a video on youtube



## Setup

```terminal
clone [path-to-repo]
cd [repo]
touch api_key.txt
touch channel_list.json
```

Edit the files called ```api_key.txt``` and ```channel_list.json``` that look like this

```txt
TheRaw4piKeyThatY0uGetFromGoogle
```

```json
[
    {"channel_id": "UCv_vLHiWVBh_FR9vbeuiY-A", "channel_name": "Historia Civilis"},
    {"channel_id": "UC2C_jShtL725hvbm1arSV9w", "channel_name": "CGP Grey"},
    {"channel_id": "UCSPLhwvj0gBufjDRzSQb3GQ", "channel_name": "Bobby Broccoli"},
    {"channel_id": "UCuVLG9pThvBABcYCm7pkNkA", "channel_name": "Climate Town"},
]
```

Then on a terminal run

```terminal
python3 youtube-notification-system.py
```