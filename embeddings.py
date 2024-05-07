from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from agents import Custom_agent
from typing import Optional
import pandas as pd
import numpy as np
import textract 
import os
import re


class EmbeddingsCSV:
    def __init__(self, csv_file='embeddings.csv'):
        self.csv_file = csv_file
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        try:
            self.df = pd.read_csv(self.csv_file)
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=['Question Embedding', 'Question', 'Answer'])

    def update_embeddings(self):
        file_paths = self._get_files_from_folder()
        
        for i, file_path in enumerate(file_paths, 1):
            print(f"\nProcessing file {i}/{len(file_paths)}")
            
            text = self._open_file(file_path)
            # TODO error ^^^^^^^^ handeling NONE

            text_chunks = self._split_text(text)
            for j, chunk in enumerate(text_chunks, 1):
                print(f"Processing chunk {j}/{len(text_chunks)}")
    
                qa_pairs = self._create_questions_and_answers(chunk)
                if qa_pairs != None:
                    for question, answer in qa_pairs:
                        print(question, answer)
                        question_embedding = self._embed_question(question)
                        
                        # Append the question, its embedding, and the answer to the DataFrame
                        new_row = {
                            'Question Embedding': question_embedding,
                            'Question': question,
                            'Answer': answer
                        }
                        self.df = self.df._append(new_row, ignore_index=True)

                print(f"Saving chunk {j}/{len(text_chunks)} embeddings")
                self.df.to_csv(self.csv_file, index=False)
                

    def search_question_answer_similarity_pairs(self, questions: list[str], similarity_threshold: float) -> list[tuple[str, str, float]]:
        question_embeddings = [self._embed_question(question) for question in questions]

        # Convert the stored embeddings from strings to numpy arrays
        stored_embeddings = [np.fromstring(embedding_str.strip('[]'), sep=' ') for embedding_str in self.df['Question Embedding'].tolist()]
        
        question_answers_and_similarities = []
        for question_embedding in question_embeddings:
            similarities = cosine_similarity([question_embedding], stored_embeddings)[0]

            indices = [i for i, sim in enumerate(similarities) if sim > similarity_threshold]

            for index in indices:
                question_answers_and_similarities.append((self.df.iloc[index]['Question'] , self.df.iloc[index]['Answer'], similarities[index]))
        question_answers_and_similarities.sort(key=lambda x: x[2], reverse=True)
        return question_answers_and_similarities

    def _get_files_from_folder(self) -> list:
        folder_path = os.path.join(os.getcwd(), 'files')
        lsit_of_paths = []
        # Check if the folder exists
        if not os.path.exists(folder_path):
            print(f"The folder {folder_path} does not exist. create it and put documents there!")
            return None
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                lsit_of_paths.append(file_path)
        return lsit_of_paths

    def _open_file(self, file_path) -> Optional[str]:
        try:
            text = textract.process(file_path)
            return text.decode('utf-8')
        except Exception as e:
            print(f"An error occurred while extracting text from {file_path}: {e}")
            return None


    def _split_text(self, text, char_limit=5000, char_overlap=500) -> list[str]:
        chunks = []
        text_length = len(text)
        start_index = 0
        sentence_endings = re.compile(r'[.!?]')

        while start_index < text_length:
            end_index = start_index + char_limit

            if end_index > text_length:
                end_index = text_length

            # Find the nearest sentence-ending punctuation mark
            sentence_end_match = sentence_endings.search(text, end_index)

            # Extend the chunk to include the complete sentence if possible
            if sentence_end_match:
                end_index = sentence_end_match.end()


            chunk = text[start_index:end_index].strip()
            chunks.append(chunk)
            start_index += char_limit - char_overlap

            # Just to be sure
            if start_index >= text_length:
                break

        return chunks


    def _create_questions_and_answers(self, chunk) -> Optional[list[tuple[str,str]]]:
        instruction = """You are an advanced algorithm. Upon receiving a text,
        your role is to generate a list of tuples. Each tuple should contain a question
        that can be fully answered based on the provided text and a comprehensive answer
        that includes all relevant details from the text. You are required to respond ONLY
        with a correctly formatted Python list of tuples, where each tuple consists
        of a string (the question) and a detailed string (the answer), including only
        the information present in the text."""
        return Custom_agent(instruction).send_request_return_type(chunk, list)


    def _embed_question(self, question) -> np.ndarray:
        embedding = self.model.encode(question, convert_to_tensor=True)
        return embedding.numpy()




if __name__ == "__main__":
    embeddings = EmbeddingsCSV()
    #embeddings.update_embeddings()
    for i in embeddings.search_embeddings(["Waht are bees doing in a city?"], 0.3):
        print(i, "\n\n")