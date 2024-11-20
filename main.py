import textwrap
from openai import OpenAI;

class InterviewBot:
    def __init__(self, key):
        self.behavioral_questions = [];
        self.coding_questions = [];
        self.behavioral_qualifiers = [];
        self.coding_qualifiers = [];
        self.codingSolutions = [];
        self.codingTranscripts = [];
        self.BQSolutions = [];
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key = key,
        )

    def runBot(self, entry):
        self.prepareData(entry);
        codingFeedback = self.evaluateCodingInterview(self.codingSolutions, self.codingTranscripts);
        BQFeedback = self.evaluateBQInterview(self.BQSolutions);
        overall = self.evaluateOverall(codingFeedback, BQFeedback);
        return overall;

    # read candidate input (code or transcript for BQ)
    def readTextFile(self, filepath):
        solution = "";
        try:
            # open the file and read
            with open(filepath, 'r') as file:
                solution = file.read();
        except FileNotFoundError:
            return f"Error: The file '{filepath}' was not found.";
        except Exception as e:
            return f"An error occurred: {str(e)}"
        return solution;

    def prepareData(self, entry):
        # Open the file in read mode
        with open(f"{entry}.txt", "r") as file:
            # Read each line in the file
            for line in file:
                # Process or print each line
                # print(line.strip());  # .strip() removes any extra newline characters
                if line.startswith("coding_submission"):
                    # this is a coding solution file
                    # print("this is coding");
                    codingFilepath = f"{line.strip()}";
                    codingSolution = self.readTextFile(codingFilepath);
                    self.codingSolutions.append(codingSolution);
                elif line.startswith("coding_t"):
                    # this is a coding transcript file
                    codingTransFilepath = f"{line.strip()}";
                    codingScript = self.readTextFile(codingTransFilepath);
                    self.codingTranscripts.append(codingScript);
                elif line.startswith("behavioral_submission"):
                    # this is a BQ solution file
                    # print("this is behavioral");
                    BQFilepath = f"{line.strip()}";
                    BQSolution = self.readTextFile(BQFilepath);
                    self.BQSolutions.append(BQSolution);
                elif line.startswith("behavioral_qualifier"):
                    fp = f"{line.strip()}";
                    content = self.readTextFile(fp);
                    self.behavioral_qualifiers.append(content);
                elif line.startswith("coding_qualifier"):
                    fp = f"{line.strip()}";
                    content = self.readTextFile(fp);
                    self.coding_qualifiers.append(content);
                elif line.startswith("coding_question"):
                    fp = f"{line.strip()}";
                    content = self.readTextFile(fp);
                    self.coding_questions.append(content);
                elif line.startswith("behavioral_question"):
                    fp = f"{line.strip()}";
                    content = self.readTextFile(fp);
                    self.behavioral_questions.append(content);

    def evaluateCodingInterview(self, solutions, explanations):
        arr = [];
        for i in range(len(self.coding_questions)):
            question = "This is an interview coding question for the candidate:\n\n";
            question += self.coding_questions[i] + "\n\n"

            requirement = "These are the requirements of my coding questions or the candidate:";
            for j in range(len(self.coding_qualifiers)):
                requirement += self.coding_qualifiers[j] + '\n\n';

            solution = "This is the solution of an applicant. Please give me a brief feedback about his coding skill and if I should hire him.\n\n"
            solution += solutions[i];

            logicExplanation = "This is the transcript of the candidate explains his logic:\n\n";
            logicExplanation += explanations[i];  # make sure u modify it later

            prompt = question + requirement + solution + logicExplanation;

            apiResult = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-4o-mini",
            )
            fb = apiResult.choices[0].message.content;
            arr.append(fb);
        filename = "coding_evaluation.txt";
        self.writeToTxtFile(filename, arr);
        print('coding feedback len = ', len(arr), '\n');
        print('coding feedback:\n', arr);
        return arr;

    def evaluateBQInterview(self, solutions):
        arr = [];
        requirements = "These are the requirements of the behavioral question(s) for the candidate:\n";
        for j in range(len(self.behavioral_qualifiers)):
            requirements += self.behavioral_qualifiers[j] + '\n\n';
        for i in range(len(self.behavioral_questions)):
            question = "This is the interview behavioral question for the candidate:\n\n";
            question += self.behavioral_questions[i] + "\n\n";
            solution = "This is the answer of an applicant. Is he a good fit for my company based on his answer?\n\n";
            solution += solutions[i];
            # openai api call
            prompt = requirements + question + solution;
            apiResult = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-4o-mini",
            )
            fb = apiResult.choices[0].message.content;
            arr.append(fb);
        filename = "BQ_evaluation.txt";
        self.writeToTxtFile(filename, arr);
        print('BQ feedback len = ', len(arr), '\n');
        print('BQ feedback:\n', arr);
        return arr;

    def evaluateOverall(self, codingFeedback, BQFeedback):
        prompt = (
            "Based on the following feedbacks generated by you, do you think I should hire the candidate as a new grad software engineer?"
            " at the end of the answer you will generate, please also give me a yes or no.\n\n");
        codingfbHeader = "the followings are the coding feedbacks:\n\n";
        prompt += codingfbHeader;
        for i in range(len(codingFeedback)):
            prompt += codingFeedback[i] + '\n\n';
        bqfbHeader = "the followings are the behavioral feedbacks:\n\n";
        prompt += bqfbHeader;
        for i in range(len(BQFeedback)):
            prompt += BQFeedback[i] + '\n\n';
        apiResult = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini",
        )
        fb = apiResult.choices[0].message.content;
        self.writeToTxtFile('overall_Chatgpt_evaluation.txt', fb);
        return fb;

    def writeToTxtFile(self, filename, content):
        # Open the file in write mode ('w')
        if isinstance(content, str):
            with open(filename, 'w') as file:
                file.write(content);
        elif isinstance(content, list):
            with open(filename, "w") as file:
                for single in content:
                    file.write(single + "\n\n")

# # Import the array from data.py;
# behavioral_questions = [];
# coding_questions = [];
# behavioral_qualifiers = [];
# coding_qualifiers = [];
# codingSolutions = [];
# codingTranscripts = [];
# BQSolutions = [];
#
# apiKey = "";
#
# client = OpenAI(
#     # This is the default and can be omitted
#     api_key = apiKey,
# )
#
# def runBot(entry):
#     prepareData(entry);
#     codingFeedback = evaluateCodingInterview(codingSolutions, codingTranscripts);
#     BQFeedback = evaluateBQInterview(BQSolutions);
#     overall = evaluateOverall(codingFeedback, BQFeedback);
#     return overall;
#
# # read candidate input (code or transcript for BQ)
# def readTextFile(filepath):
#     solution = "";
#     try:
#         #open the file and read
#         with open(filepath, 'r') as file:
#             solution = file.read();
#     except FileNotFoundError:
#         return f"Error: The file '{filepath}' was not found.";
#     except Exception as e:
#         return f"An error occurred: {str(e)}"
#     return solution;
#
# def prepareData(entry):
#     # Open the file in read mode
#     with open(f"{entry}.txt", "r") as file:
#         # Read each line in the file
#         for line in file:
#             # Process or print each line
#             # print(line.strip());  # .strip() removes any extra newline characters
#             if line.startswith("coding_submission"):
#                 # this is a coding solution file
#                 # print("this is coding");
#                 codingFilepath = f"{line.strip()}";
#                 codingSolution = readTextFile(codingFilepath);
#                 codingSolutions.append(codingSolution);
#             elif line.startswith("coding_t"):
#                 # this is a coding transcript file
#                 codingTransFilepath = f"{line.strip()}";
#                 codingScript = readTextFile(codingTransFilepath);
#                 codingTranscripts.append(codingScript);
#             elif line.startswith("behavioral_submission"):
#                 # this is a BQ solution file
#                 # print("this is behavioral");
#                 BQFilepath = f"{line.strip()}";
#                 BQSolution = readTextFile(BQFilepath);
#                 BQSolutions.append(BQSolution);
#             elif line.startswith("behavioral_qualifier"):
#                 fp = f"{line.strip()}";
#                 content = readTextFile(fp);
#                 behavioral_qualifiers.append(content);
#             elif line.startswith("coding_qualifier"):
#                 fp = f"{line.strip()}";
#                 content = readTextFile(fp);
#                 coding_qualifiers.append(content);
#             elif line.startswith("coding_question"):
#                 fp = f"{line.strip()}";
#                 content = readTextFile(fp);
#                 coding_questions.append(content);
#             elif line.startswith("behavioral_question"):
#                 fp = f"{line.strip()}";
#                 content = readTextFile(fp);
#                 behavioral_questions.append(content);
#
# def evaluateCodingInterview(solutions, explanations):
#     arr = [];
#     for i in range(len(coding_questions)):
#         question = "This is an interview coding question for the candidate:\n\n";
#         question += coding_questions[i] + "\n\n"
#
#         requirement = "These are the requirements of my coding questions or the candidate:";
#         for j in range(len(coding_qualifiers)):
#             requirement += coding_qualifiers[j] + '\n\n';
#
#         solution = "This is the solution of an applicant. Please give me a brief feedback about his coding skill and if I should hire him.\n\n"
#         solution += solutions[i];
#
#         logicExplanation = "This is the transcript of the candidate explains his logic:\n\n";
#         logicExplanation += explanations[i]; #make sure u modify it later
#
#         prompt = question + requirement + solution + logicExplanation;
#
#         apiResult = client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 }
#             ],
#             model="gpt-4o-mini",
#         )
#         fb = apiResult.choices[0].message.content;
#         arr.append(fb);
#     filename = "coding_evaluation.txt";
#     writeToTxtFile(filename, arr);
#     print('coding feedback len = ', len(arr), '\n');
#     print('coding feedback:\n', arr);
#     return arr;
#
# def evaluateBQInterview(solutions):
#     arr = [];
#     requirements = "These are the requirements of the behavioral question(s) for the candidate:\n";
#     for j in range(len(behavioral_qualifiers)):
#         requirements += behavioral_qualifiers[j] + '\n\n';
#     for i in range(len(behavioral_questions)):
#         question = "This is the interview behavioral question for the candidate:\n\n";
#         question += behavioral_questions[i] + "\n\n";
#         solution = "This is the answer of an applicant. Is he a good fit for my company based on his answer?\n\n";
#         solution += solutions[i];
#         # openai api call
#         prompt = requirements + question + solution;
#         apiResult = client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 }
#             ],
#             model="gpt-4o-mini",
#         )
#         fb = apiResult.choices[0].message.content;
#         arr.append(fb);
#     filename = "BQ_evaluation.txt";
#     writeToTxtFile(filename, arr);
#     print('BQ feedback len = ', len(arr), '\n');
#     print('BQ feedback:\n', arr);
#     return arr;
#
# def evaluateOverall(codingFeedback, BQFeedback):
#     prompt = ("Based on the following feedbacks generated by you, do you think I should hire the candidate as a new grad software engineer?"
#               " at the end of the answer you will generate, please also give me a yes or no.\n\n");
#     codingfbHeader = "the followings are the coding feedbacks:\n\n";
#     prompt += codingfbHeader;
#     for i in range(len(codingFeedback)):
#         prompt += codingFeedback[i] + '\n\n';
#     bqfbHeader = "the followings are the behavioral feedbacks:\n\n";
#     prompt += bqfbHeader;
#     for i in range(len(BQFeedback)):
#         prompt += BQFeedback[i] + '\n\n';
#     apiResult = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt,
#             }
#         ],
#         model="gpt-4o-mini",
#     )
#     fb = apiResult.choices[0].message.content;
#     writeToTxtFile('overall_Chatgpt_evaluation.txt', fb);
#     return fb;
#
# def writeToTxtFile(filename, content):
#     # Open the file in write mode ('w')
#     if (isinstance(content, str)):
#         with open(filename, 'w') as file:
#             file.write(content);
#     elif (isinstance(content, list)):
#         with open(filename, "w") as file:
#             for single in content:
#                 file.write(single + "\n\n")
#
# def evaluateCodingBad():
#     fp = "coding_submission_bad.txt";
#     solution = readTextFile(fp);
#     fp = "bad_coding_transcript.txt";
#     logic = readTextFile(fp)
#     feedbackArr = evaluateCodingInterview([solution], [logic]);
#     return feedbackArr;
#
# def evaluateCodingOk():
#     fp = "coding_submission_ok.txt";
#     solution = readTextFile(fp);
#     fp = "coding_transcript1.txt";
#     logic = readTextFile(fp)
#     feedbackArr = evaluateCodingInterview([solution], [logic]);
#     return feedbackArr;
#
# def evaluateCodingOptimal():
#     fp = "coding_submission_opt.txt";
#     solution = readTextFile(fp);
#     fp = "coding_transcript_opt.txt";
#     logic = readTextFile(fp)
#     feedbackArr = evaluateCodingInterview([solution], [logic]);
#     return feedbackArr;
#
# def evaluateBqGood():
#     fp = "behavioral_submission_good.txt";
#     solution = readTextFile(fp);
#     feedbackArr = evaluateBQInterview([solution]);
#     return feedbackArr;
#
# def testTrans():
#     filepath = "mock_transcript.txt";
#     content = readTextFile(filepath);
#     #print("content:", content);
#     header = ("This is a unedited mock interview transcript (from Youtube) between a Meta intern software engineer and a "
#               "senior Google software engineer. Please analyze this transcript and give me some evaluation of how the "
#               "candidate did in this mock interview. \n\n");
#     prompt = header + content;
#     apiResult = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt,
#             }
#         ],
#         model="gpt-4o-mini",
#     )
#     result = apiResult.choices[0].message.content;
#     writeToTxtFile('mock_interview_Chatgpt_evaluation.txt', result);
#     return result;

# # evaluate coding performance
# codingFilepath = "coding_submission1.txt";
# codingSolution = readTextFile(codingFilepath);
# codingFeedback = evaluateCodingInterview([codingSolution]);
# #print("coding feedback:", textwrap.fill(codingFeedback[0], width=88));
#
# # evaluate BQ performance
# BQFilepath = "behavioral_submission1.txt";
# BQSolution = readTextFile(BQFilepath);
# BQFeedback = evaluateBQInterview([BQSolution]);
# #print("BQ feedback:", textwrap.fill(BQFeedback[0], width=88));
#
# # overall feedbacks
# overallFeedback = evaluateOverall(codingFeedback, BQFeedback);
# print("overallFeedback:\n", overallFeedback);

# overallFeedback = runBot("entry");
# print("overall feedback:\n", overallFeedback);

# #test bad coding response 2 sum
# badCodingFb = evaluateCodingBad();
# for i in range(len(badCodingFb)):
#     print("bad coding feedback:\n", textwrap.fill(badCodingFb[i], width=88));

# okCodingFb = evaluateCodingOk();
# for i in range(len(okCodingFb)):
#     print("ok coding feedback:\n", textwrap.fill(okCodingFb[i], width=88));

# optCodingFb = evaluateCodingOptimal();
# for i in range(len(optCodingFb)):
#     print("optimal coding feedback:\n", textwrap.fill(optCodingFb[i], width=88));

# goodBqFb = evaluateBqGood();
# for i in range(len(goodBqFb)):
#     print("good BQ feedback:\n", textwrap.fill(goodBqFb[i], width=88));

# #test AI bot with youtube mock interview transcript
# mockEvalResult = testTrans();

key = "";
script = "entry";
bot = InterviewBot(key);
bot.runBot(script);