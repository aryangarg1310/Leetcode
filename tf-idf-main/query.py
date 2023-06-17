from flask import Flask, jsonify
import math
import re
import os

from flask import Flask
app = Flask(__name__)
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

def load_vocab():
    vocab = {}
    with open(os.path.abspath('./tfidf/vocab.txt'), 'r', encoding='utf-8') as f:
        vocab_terms = f.readlines()
    with open(os.path.abspath('./tfidf/idf-values.txt'), 'r', encoding='utf-8') as f:
        idf_values = f.readlines()
    
    for (term,idf_value) in zip(vocab_terms, idf_values):
        vocab[term.strip()] = int(idf_value.strip())
    
    return vocab

def load_documents():
    documents = []
    with open(os.path.abspath('./tfidf/documents.txt'), 'r', encoding='utf-8') as f:
        documents = f.readlines()
    documents = [document.strip().split() for document in documents]

    print('Number of documents: ', len(documents))
    # print('Sample document: ', documents[0])
    return documents

def load_inverted_index():
    inverted_index = {}
    with open(os.path.abspath('./tfidf/inverted-index.txt'), 'r', encoding='utf-8') as f:
        inverted_index_terms = f.readlines()

    for row_num in range(0,len(inverted_index_terms),2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num+1].strip().split()
        inverted_index[term] = documents
    
    print('Size of inverted index: ', len(inverted_index))
    return inverted_index

def load_link_of_qs():
    links = []
    with open(os.path.abspath('../Qdata/Qindex.txt'), 'r', encoding='latin-1') as f:
        links = f.readlines()
    return links

def load_title_of_qs():
    headings = []
    with open(os.path.abspath('../Qdata/index.txt'), 'r', encoding='latin-1') as f:
        headings = f.readlines()

    cleaned_headings = []
    for heading in headings:
        # Remove leading numbers
        heading = re.sub(r'^\d+\.\s*', '', heading)

        cleaned_headings.append(heading)

    return cleaned_headings

Qlink = load_link_of_qs()
Qtitle = load_title_of_qs()
vocab_idf_values = load_vocab()
documents = load_documents()
inverted_index = load_inverted_index()


def get_tf_dictionary(term):
    tf_values = {}
    if term in inverted_index:
        for document in inverted_index[term]:
            if document not in tf_values:
                tf_values[document] = 1
            else:
                tf_values[document] += 1
                
    for document in tf_values:
        tf_values[document] /= len(documents[int(document)])
    
    return tf_values

def get_idf_value(term):
    return math.log(len(documents)/vocab_idf_values[term])

def calculate_sorted_order_of_documents(query_terms):
    potential_documents = {}
    for term in query_terms:
        if term not in vocab_idf_values:
            continue
        tf_values_by_document = get_tf_dictionary(term)
        idf_value = get_idf_value(term)

        for document in tf_values_by_document:
            if document not in potential_documents:
                potential_documents[document] = tf_values_by_document[document] * idf_value
            potential_documents[document] += tf_values_by_document[document] * idf_value

    for document in potential_documents:
        potential_documents[document] /= len(query_terms)

    potential_documents = dict(sorted(potential_documents.items(), key=lambda item: item[1], reverse=True))
    result = []
    if len(potential_documents) == 0:
        result.append("No matching question found. Please search with more relevant terms.")
    else:
        result.append("The Question links in Decreasing Order of Relevance are:")
        for document_index in potential_documents:
            result.append({
                "Question Name": Qtitle[int(document_index) - 1][:-1],
                "Question Link": Qlink[int(document_index) - 1][:-2],
                "Score": potential_documents[document_index]
            })

    return result



# query_string = input('Enter your query: ')
# query_terms = [term.lower() for term in query_string.strip().split()]

# print(query_terms)
# print(calculate_sorted_order_of_documents(query_terms))


app.config['SECRET_KEY'] = 'your-secret-key'
class SearchForm(FlaskForm):
    search = StringField('Enter your search term')
    submit = SubmitField('Search')
    
@app.route("/", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    result = []
    if form.validate_on_submit():
        query = form.search.data

        query_terms = [term.lower() for term in query.strip().split()]
        results = calculate_sorted_order_of_documents(query_terms)[:10:] 
    return render_template('index.html', form=form, results = results)

if __name__=="_main":
    app.run(debug=True)
        