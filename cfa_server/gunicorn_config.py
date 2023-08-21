import multiprocessing

bind = "127.0.0.1:9002"  # The IP and port Gunicorn will listen on
workers = multiprocessing.cpu_count() * 2 + 1  # Number of worker processes