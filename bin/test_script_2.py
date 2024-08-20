import argparse

def main(args):
    print(f"Py script: A: {args.A}")
    print(f"Py script: B: {args.B}")
    print(f"Py script: C: {args.C}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--A')
    parser.add_argument('--B')
    parser.add_argument('--C')
    args = parser.parse_args()
    main(args)