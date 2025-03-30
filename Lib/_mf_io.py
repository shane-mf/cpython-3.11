def mf_open(file, flags):
    print(f"mf_open: {file}, {flags}")

    import traceback
    print("Call stack:")
    for frame in traceback.extract_stack():
        print(f"  File \"{frame.filename}\", line {frame.lineno}, in {frame.name}")
    return 1
