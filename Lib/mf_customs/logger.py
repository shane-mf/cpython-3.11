def debug(message):
    print(f"DEBUG-MF: {message}")
    import traceback
    print("Call stack:")
    for frame in traceback.extract_stack():
        print(f"  File \"{frame.filename}\", line {frame.lineno}, in {frame.name}")

