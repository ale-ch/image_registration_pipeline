import argparse
import os 

def main(args):
    path = '/Users/alessiochiodin/Documents/Programming/Tests/image_registration_pipeline/prints'
    filename = 'test_script_1_output.txt'
    with open(os.path.join(path, filename), 'w') as f:
        f.write(f"Py script: A: {args.A}")
        f.write('\n')
        f.write(f"Py script: B: {args.B}")
        f.write('\n')
        f.write(f"Py script: C: {args.C}")

        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--A')
    parser.add_argument('--B')
    parser.add_argument('--C')
    args = parser.parse_args()
    main(args)