# # import os
# # from dotenv import load_dotenv
# # from langchain_openai import ChatOpenAI
# # from langchain_core.messages import HumanMessage

# # def chain_joke_to_dark():
# #     load_dotenv()
# #     api_key = os.getenv("OPENAI_API_KEY")
# #     llm = ChatOpenAI(
# #         api_key=api_key,
# #         model="gpt-3.5-turbo"
# #     )

# #     joke_prompt = "Tell me a funny joke."
# #     joke_response = llm.invoke([HumanMessage(content=joke_prompt)])
# #     joke = joke_response.content.strip()

# #     dark_prompt = f"Take this joke and twist it to make it +18 jokes, it can contain swear words and anything you want:\n\n{joke}"
# #     dark_response = llm.invoke([HumanMessage(content=dark_prompt)])
# #     dark_joke = dark_response.content.strip()

# #     return joke, dark_joke

# # joke, dark_joke = chain_joke_to_dark()

# # print(joke)
# # print(dark_joke)

# import io
# import sys
# import traceback

# stdout = io.StringIO()
# stderr = io.StringIO()

# local_env = {}

# code = """
# def add(a, b):
#     return a + b
# """

# test = """
# assert add(1, 2) == 3
# assert add(3, 5) == 9
# """

# orig_stdout = sys.stdout
# orig_stderr = sys.stderr

# sys.stdout = stdout
# sys.stderr = stderr

# sys.stdout = orig_stdout
# sys.stderr = orig_stderr

# try:

#     exec(code, {}, local_env)
#     exec(test, {}, local_env)
#     print("Passed tests")

# except:
#     print("failed tests") 

import unittest
import numpy as np

def compute_dot_product(a, b):
    return np.dot(a, b)

class TestDotProduct(unittest.TestCase):
    def test_positive_numbers(self):
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        self.assertEqual(compute_dot_product(a, b), 32)

    def test_with_zero(self):
        a = np.array([0, 0, 0])
        b = np.array([4, 5, 6])
        self.assertEqual(compute_dot_product(a, b), 0)

    def test_negative_numbers(self):
        a = np.array([-1, -2, -3])
        b = np.array([4, 5, 6])
        self.assertEqual(compute_dot_product(a, b), -322)

    def test_mixed_signs(self):
        a = np.array([1, -2, 3])
        b = np.array([-4, 5, -6])
        self.assertEqual(compute_dot_product(a, b), -32)

    def test_different_lengths(self):
        a = np.array([1, 2])
        b = np.array([3, 4, 5])
        with self.assertRaises(ValueError):
            np.dot(a, b)  # NumPy raises ValueError for shape mismatch

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDotProduct)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    # print(result)
