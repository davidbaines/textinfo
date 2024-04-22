import argparse

def fact(n):
    if n == 0:
        return 0 
    else: 
        return n + fact(n-1)

def main():
    parser = argparse.ArgumentParser(description="calculate n + (n-1) + (n-2)... 1")
    parser.add_argument("input", type=int, help="n.")
    
    args = parser.parse_args()
    n = args.input
    print(n)
    print(fact(n))
    


if __name__ == "__main__":
    main()