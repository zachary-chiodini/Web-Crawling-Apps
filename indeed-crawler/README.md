Probably, does not work on Mac OS.

Run "python build.py" in the indeed-crawler directory to compile the program. Afterwards, the indeed-crawler/dist/driver, indeed-crawler/dist/fasttext-model, and indeed-crawler/dist/icon folders, and the indeed-crawler/dist/q_and_a.json file must be copied and pasted to the indeed-crawler/dist/job-crawler-beta directory. The resuting indeed-crawler/dist/job-crawler-beta/job-crawler-beta.exe is equiped with a graphical user interface.

The program uses Selenium to access the job search website and a word embedding model to answer screening questions, based on the q_and_a.json file and user input. The user must have a job search account and their resume uploaded to the account before running the program to begin applying to jobs. 

The fasstext word embedding model can be downloaded [here](https://fasttext.cc/docs/en/crawl-vectors.html). The program is currently hardcoded to use the cc.en.300.bin model. This model must be stored in the indeed-crawler/fasttext-model directory if running main.py, or the indeed-crawler/dist/job-crawler-beta/fasttext-model directory if running the compiled executable.

Due to the dynamic nature of web development, the program is not garanteed to function properly and may need to be edited from time to time to restore functionality. A future endeavor will be to utilize an original machine learning model to enable the program to work on any website or to at least accept minute changes to a given website, but for now the program is hardcoded to search for specific tags and patterns on a specific website's source code.

```python
(venv) python main.py
```
