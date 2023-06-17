# read the index.txt and prepare documents, vocab , idf
import chardet
import string
import os
def find_encoding(fname):
    r_file = open(fname, 'rb').read()
    result = chardet.detect(r_file)
    charenc = result['encoding']
    return charenc

filename = os.path.abspath('./Qdata/index.txt')
my_encoding = find_encoding(filename)
dir_name = os.path.abspath('./Qdata')
num_questions=2405

lines=[]


print("processing question data ........")
for i in range(1,num_questions+1):
    doc = ""
    with open(dir_name+'/'+str(i)+'/'+str(i)+'.txt','r',encoding=my_encoding) as f:
        for line in f.readlines():
            # print(line)
            if(line=="  Example 1:\n"):
                # print("hey")
                break
            doc += line
        
        lines.append(doc)
            # lines.append(lines)
    
print("question data processed successfully!")

print("processing text data.........")
def preprocess(document_text):
    # remove the leading numbers from the string, remove not alpha numeric characters, make everything lowercase
    terms = [term.lower() for term in document_text.strip().split()[1:]]
    return terms
print("text data processed successfully!")
vocab = {}
documents = []
accepted_char=list(string.ascii_lowercase)
accepted_char.append('-')
accepted_char.append('(')
accepted_char.append(')')
print(accepted_char)
for index, line in enumerate(lines):
    # read statement and add it to the line and then preprocess
    tokens = preprocess(line)
    documents.append(tokens)
    tokens = set(tokens)
    for token in tokens:
        flag=True
        for chars in token:
            # print(chars)
            if chars not in accepted_char:
                flag=False
                break
        if flag==False:
            continue
        if token not in vocab:
            vocab[token] = 1
        else:
            vocab[token] += 1

# reverse sort the vocab by the values
vocab = dict(sorted(vocab.items(), key=lambda item: item[1], reverse=True))

print("vocabulary created!")

print('Number of documents: ', len(documents))
print('Size of vocab: ', len(vocab))
print('Example document: ', documents[0])

# save the vocab in a text file
with open(os.path.abspath('./tf-idf-main/tfidf/vocab.txt'), 'w', encoding='utf-8') as f:
    for key in vocab.keys():
        f.write("%s\n" % key)
print("vocab saved successfully!")
# save the idf values in a text file
with open(os.path.abspath('./tf-idf-main/tfidf/idf-values.txt'), 'w', encoding='utf-8') as f:
    for key in vocab.keys():
        f.write("%s\n" % vocab[key])
print("idf values saved successfully!")
# save the documents in a text file
try:
    with open(os.path.abspath('./tf-idf-main/tfidf/documents.txt'), 'w', encoding='utf-8') as f:
        for document in documents:
            f.write("%s\n" % ' '.join(document))
    print("Documents saved successfully!")
except Exception as e:
    print("An error occurred:", str(e))

    
inverted_index = {}
for index, document in enumerate(documents):
    for token in document:
        if token not in inverted_index:
            inverted_index[token] = [index]
        else:
            inverted_index[token].append(index)

# save the inverted index in a text file
with open(os.path.abspath('./tf-idf-main/tfidf/inverted-index.txt'), 'w', encoding='utf-8') as f:
    for key in inverted_index.keys():
        f.write("%s\n" % key)
        f.write("%s\n" % ' '.join([str(doc_id) for doc_id in inverted_index[key]]))
