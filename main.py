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

script = "entry";
bot = InterviewBot();
bot.runBot(script);