import random
import json
import math
import os


"""
Function to generate random cipher given an alphabet.

Inputs:
- alphabet: List of characters in the alphabet

Outputs:
- permuted: Random list of unique characters in the alphabet
"""


def permuteAlph(alphabet):
    """
    Returns a randomly permuted version of the alphabet.
    """
    permuted = random.sample(alphabet, len(alphabet))
    return permuted


"""
Function to encipher a message.

Inputs:
- message (str): The message to encipher
- cipher (list): The cipher which is a list of characters to use on the message
- alphabet (list): A list of characters making up the original alphabet

Outputs:
- encMessage (str): The enciphered message
"""


def encipher(message, cipher, alphabet):

    cipherMap = {}
    for i, char in enumerate(alphabet):
        try:
            # each character in cipherMap corresponds to a character in the
            # cipher according to index
            cipherMap[char] = cipher[i]
        except KeyError:
            continue

    messageList = list(message)  # convert string to list to mutate

    for i, char in enumerate(messageList):
        try:
            messageList[i] = cipherMap[char]
        except KeyError:
            continue

    # convert the list to string at the end
    encMessage = ''.join(messageList)

    return encMessage


"""
Function to swap two random letters of a given cipher.

Inputs:
- cipher (str): The reverse cipher whose letters have to be swapped

Outputs:
- cipherList (str): A new reverse cipher with two randomly swapped letters
"""


def swapCipher(cipher):
    cipherList = list(cipher)
    i, j = random.sample(range(len(cipherList)), 2)
    cipherList[i], cipherList[j] = cipherList[j], cipherList[i]
    return cipherList


"""
Function to process transition matrix.

Inputs:
- readFile: File name to be read
        Note:
        - Must give full file path
        - Must be a text file

Outputs:
- writeFile: File name to be written to
        Note:
        - Must give full file path
        - Must be a JSON file
"""


def transitionMatrix(readFile, writeFile, alphabet):
    with open(readFile, 'r') as reader, open(writeFile, 'w') as writer:

        # initializing matrix of 2 dimensional dictionary
        M = {c1: {c2: 0.0 for c2 in alphabet} for c1 in alphabet}

        # loop over each line
        for line in reader:
            line = line.rstrip()  # remove newline character
            if len(line) > 0:  # check if line has any real characters
                for c in range(len(line)-1):  # only go till 2nd last character
                    try:
                        # increment each transition
                        c1 = line[c]
                        c2 = line[c+1]
                        M[c1][c2] += 1
                    # handle characters that are not in alphabet by skipping over
                    except KeyError:
                        continue
        total = 0.0
        # Normalize the counts to probabilities
        for c1 in M:
            total += sum(M[c1].values())
            # for c2 in M[c1]:
            #     M[c1][c2] /= total
        for c1 in M:
            for c2 in M[c1]:
                M[c1][c2] /= total

        # replace all 0.0 probabilities w/ e-20
        for key, values in M.items():
            for key2, value2 in values.items():
                if value2 == 0.0:
                    M[key][key2] = math.exp(-20)

        # storing it in a json file to make reading easier
        json.dump(M, writer)


"""
Function to calculate the acceptance probability.

Inputs:
- X: List of characters for current reverse cipher
- Y: List of characters for new reverse cipher
- message: String containing a message
- M: 2-dimensional dictionary containing transitions of letters in given alphabet
- alphabet: List of characters in the alphabet being used

Outputs:
- acceptanceProbability: Float number which is the acceptance probability
"""


def acceptProb(X, Y, encipheredMessage, M, alphabet):

    unscrambledX = encipher(encipheredMessage, alphabet,
                            X)  # unscramble using cipher X
    unscrambledY = encipher(encipheredMessage, alphabet,
                            Y)  # unscramble using cipher Y
    logProbX = 0.0
    logProbY = 0.0

    # loop over unscrambled message taking sum of logs of transition probabilities
    for i in range(len(unscrambledX)-1):
        try:
            # calculate log probabilities of consecutive characters in reverse cipher X
            logProbX += math.log(M[unscrambledX[i]][unscrambledX[i+1]])
        except KeyError:
            continue
    for i in range(len(unscrambledY)-1):
        try:
            # calculate log probabilities of consecutive characters in reverse cipher Y
            logProbY += math.log(M[unscrambledY[i]][unscrambledY[i+1]])
        except KeyError:
            continue

    # difference to be used to calculate acceptance probability to avoid math error
    diff = logProbY - logProbX

    # Avoiding overflow by comparing values in log space
    if diff > 0:
        acceptanceProbability = 1.0
    else:
        acceptanceProbability = math.exp(diff)  # e^<any negative value> is < 1

    return acceptanceProbability


"""
Function to find the log probability given a cipher.

Inputs:
- cipher: A list of characters for one cipher
- encipheredMessage: An enciphered message represented as a string
- M: A nested dictionary containing the transition probabilities in the alphabet
     using a pre-defined text of English Language
- alphabet: A list of characters that are used in the message

Outputs:
- logProb: A float representing the sum of logs of each character's transition
           to a subsequent character based on transition matrix M
"""


def measure(cipher, encipheredMessage, M, alphabet):
    logProb = 0.0
    unscrambled = encipher(encipheredMessage, alphabet, cipher)
    for i in range(len(unscrambled)-1):
        try:
            logProb += math.log(M[unscrambled[i]][unscrambled[i+1]])
        except KeyError:
            continue
    return logProb


"""
Function to run the Metropolis-Hastings algorithm with max iterations pre-defined

Inputs:
- alphabet: A list of characters that are used in the message
- encipheredMessage: An enciphered message represented as a string
- M: A nested dictionary containing the transition probabilities in the alphabet
     using a pre-defined text of English Language

Outputs:
- bestRevCipher: A list of characters that are found to be the best reverse
                 cipher by the metropolis-hastings algorithm
"""


def metropolisHastings(alphabet, encipheredMessage, M, max_iter=10000):

    # initial cipher
    currCipher = permuteAlph(alphabet)

    # current best cipher is initial cipher
    bestRevCipher = currCipher.copy()

    for i in range(max_iter):
        nextCipher = swapCipher(currCipher).copy()  # avoid pointer issue
        acceptanceProbability = acceptProb(
            currCipher, nextCipher, encipheredMessage, M, alphabet)
        # check to accept new cipher
        if acceptanceProbability > random.uniform(0.0, 1.0):
            currCipher = nextCipher.copy()  # new reverse cipher
            # check for best cipher
            if measure(currCipher, encipheredMessage, M, alphabet) > measure(bestRevCipher, encipheredMessage, M, alphabet):
                bestRevCipher = currCipher.copy()
    return bestRevCipher


if __name__ == "__main__":

    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                ' ', ',', '.', ':', ';', '!', '?', '/']

    message = """
    Sarah is a cheerful and enthusiastic student who eagerly attends school
    each day. She thrives on the opportunity to expand her knowledge and
    discover new things. Among all her subjects, math holds a special place
    in her heart. The joy of solving equations and understanding mathematical
    concepts fills her with a sense of accomplishment. Alongside her academic
    pursuits, Sarah values the friendships she has cultivated at school.
    During recess, she and her friends engage in various games and activities,
    laughing and sharing stories. Outside of school hours, Sarah often immerses
    herself in the world of books, especially those that feature captivating
    tales about animals. Whether it's diving into the adventures of brave
    lions or the mischievous antics of curious monkeys, Sarah finds solace
    and excitement in the pages of her favorite stories. John is different.
    In the bustling kitchen of a vibrant restaurant, you'll find John, a
    dedicated chef whose passion for culinary excellence knows no bounds.
    With precision and creativity, John crafts mouthwatering dishes that
    tantalize the taste buds of eager customers. His culinary journey began
    in his grandmother's kitchen, where he absorbed the secrets of traditional
    cooking techniques and the importance of using fresh, quality ingredients.
    Today, armed with years of experience and a relentless drive for perfection,
    John specializes in creating exquisite pasta dishes that leave diners
    craving more. Beyond the confines of the kitchen, John is a dreamer with
    ambitious aspirations. He envisions a future where he can share his
    culinary creations in his own restaurant, a place where patrons can savor
    not only delicious food but also the warmth of hospitality and the essence
    of culinary artistry. With each dish he prepares, John takes another step
    closer to turning his dream into reality, fueled by his unwavering passion
    and dedication to the craft of cooking.
    """
    script_dir = os.path.dirname(__file__)
    cipher = permuteAlph(alphabet)
    encipheredMessage = encipher(
        message, cipher, alphabet)  # enciphered message

    # reading transition matrix
    with open(os.path.join(script_dir, 'TransitionMatrix.json')) as reader:
        M = json.load(reader)

    revCipher = metropolisHastings(alphabet, encipheredMessage, M).copy()
    print("The message is:\n", message)
    print("\n")
    print("The cipher is:\n", cipher)
    print("\n")
    print("The enciphered message is:\n", encipheredMessage)
    print("\n")
    print("The best reverse cipher is:\n", revCipher)
    print("\n")
    print("The message with this reverse cipher is:\n",
          encipher(encipheredMessage, alphabet, revCipher))
    