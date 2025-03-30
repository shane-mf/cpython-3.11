def debug(message):
    # import datetime
    import traceback
    
    with open('./mf_logger.log', 'a') as log_file:
        # timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # log_file.write(f"[{timestamp}] DEBUG-MF: {message}\n")
        log_file.write(f"DEBUG-MF: {message}\n")
        log_file.write("Call stack:\n")
        for frame in traceback.extract_stack():
            log_file.write(f"  File \"{frame.filename}\", line {frame.lineno}, in {frame.name}\n")
        log_file.write("\n")

def error(message):
    print(f"ERROR-MF: {message}")
    import traceback
    print("Call stack:")
    for frame in traceback.extract_stack():
        print(f"  File \"{frame.filename}\", line {frame.lineno}, in {frame.name}")
