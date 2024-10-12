"""
File Name: _isPrime.py

Author: Poorva Sharma (100934359)

Date: 11 October'2024

Description: This file contains code which tells whether a number is Prime or not 
and if the number is not prime it tells its factors. Also it tells the prime number before
and after to that number.

"""

factors = []

def is_prime(num, flag):
    result = True
    for i in range(2,num):
        if num % i == 0:
            result = False
            if flag:
                factors.append(i)
    
    return result

def preceding_prime(num):
    for i in range(num, 1, -1):
        result = is_prime(i, False)
        if result:
            return i
        
    return 2

def succeding_prime(num):
    i = num
    while True:
        result = is_prime(i, False)
        if result:
            return i
        else:
            i+=1

if __name__ == "__main__":
    while True:     
        num = int(input("Enter positive whole number: "))
        if (num <= 0):
            print("Please enter positive whole number: ")
        elif (num > 0):
            
            res1 = is_prime(num, True)
            res2 = preceding_prime(num - 1)
            res3 = succeding_prime(num + 1)
            
            print(f"The prime number before {num} is {res2}")
            if res1:
                print(f"{num} is a prime number.")
            else:
                print(f"{num} is not a prime number. Its factors are {factors}")
            
            print(f"The prime number after {num} is {res3}")
            
            break