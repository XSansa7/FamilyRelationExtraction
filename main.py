import os
import re
import numpy as np
import pickle
from collections import Counter

paragraph = []
sentences = []
#############################################################################
#                       functions
#############################################################################
def add_node(p, li, children):
    for i in li:
        if i[0] == p[-1]:
            add_node(i,li, children)
            if children[i[0]] == 1:
                p.extend(i[1:])
                li.remove(i)

def build_tree(li):
    has_child = []
    has_parent = set()
    root = []
    for i in li:
        for j in li:
            if i[0] == j[-1] and i[-1] == j[0]:
                if i[1] == 'mod':
                    j[1] += '-1'
                    j[0] = i[0]
                    j[-1] = i[-1]

                    li.remove(i)
                    break
                else:
                    i[1] += '-1'
                    i[0] = j[0]
                    i[-1] = j[-1]

                    li.remove(j)
                    break
    for i in li:
        has_child.append(i[0])
        has_parent.add(i[-1])
    child_num = Counter(has_child)
    for i in li:
        if i[0] not in has_parent:
            root.append(i)          
    for i in root:
        add_node(i, li, child_num)
    return root[0][0]


def path_from_root(node, root, li):
    if node != root:
        for i in li:
            if node in i and node!=i[0]:
                path = path_from_root(i[0],root,li)
                path.extend(i[1:i.index(node)+1])
                break              
    else:
        path = [root]
    return path

    
def find_path(s, e, li, root):
    path_s = path_from_root(s, root, li)
    path_e = path_from_root(e, root, li)
    max_common_index = min(len(path_s),len(path_e))
    for i in range(max_common_index):
        if path_s[i] != path_e[i]:
            break
    if path_s[i] == path_e[i]:
        i = i+1
    path = list(path_s[i-1:])
    path.reverse()
    for j in range(1,len(path),2):
        path[j] += '-1'
    path.extend(path_e[i:])
    return path

def patternMatch(path):
    PERSON_s= [x for x in path if x[0][0]+x[0][1:].lower() in['he','she','She','He','I','Me','me','You','you','They','they','him','her','who','Who']+god_names]

    RELATION= [x for x in path if x[0].lower() in family_relation]
    BEAR_s=[x for x in path if x[0] in['borne','bearing','bears','bear','bore','born']]

    PERSON_o=[x for x in path if x[0][0]+x[0][1:].lower() in['his','her','His','Her','Your','Their','My','whose','your','their','my']+god_names]

    BE=[x for x in path if x[0].lower() in['was','were','is','am','be','being']]

    HAVE=[x for x in path if x[0].lower() in ['have','had','has']]

    BECOME=[x for x in path if x[0].lower() in ['become','became','becomes','becoming']]
    NAME=[x for x in path if x[0].lower() in ['name']]
    CALLED=[x for x in path if x[0].lower() in ['called','named']]
    
    rules=[[PERSON_s,'appos',RELATION,'prep_of',PERSON_s]]
    rules.append([PERSON_s, 'nn', RELATION, 'poss',PERSON_o])
    rules.append([PERSON_s,'dobj', RELATION,'poss',PERSON_o])
    rules.append([PERSON_s,'nsubj-1', BEAR_s,('xcomp', PERSON_s), 'dobj', (RELATION, 'appos'), PERSON_s])
    rules.append([PERSON_s , 'nsubj-1' , BEAR_s, 'prep_to' , PERSON_s])
    rules.append([PERSON_s, 'nsubj-1', BE, 'cop', RELATION, 'prep_of', PERSON_s])
    rules.append([PERSON_s, 'nsubj-1', HAVE, 'dobj', RELATION, 'appos', PERSON_s])
    rules.append([PERSON_s, 'nsubj-1', HAVE, 'dobj', PERSON_s, 'nn', RELATION])
    
    rules.append([PERSON_s, 'nsubj-1',HAVE,'dobj',RELATION,'partmod',CALLED,'objcomp',PERSON_s])

   
    rules.append([PERSON_s, 'nsubj-1', BE, 'cop', RELATION, 'poss', PERSON_s])
    rules.append([PERSON_s, 'appos', RELATION, 'prep_of', PERSON_s, 'cc', PERSON_s])

    rules.append([PERSON_s, 'nsubj', HAVE, 'dobj', RELATION, 'prep_by', NAME, 'prep_of', PERSON_s])


    rules.append([PERSON_s, 'nsubj-1', BECOME, 'cop', RELATION, 'poss', PERSON_o])#####
    rules.append([PERSON_s, 'nsubj-1', BECOME, 'cop', RELATION, 'prep_of', PERSON_s])######
    pattern=[[0,-1,2],[0,-1,2],[0,-1,2],[[0,-1,'mother'],[0,4,'spouse'],[4,-1,'father']]]
    pattern.append([0,-1,'spouse'])
    pattern.append([0,-1,4])
    pattern.append([-1,0,4])
    pattern.append([0,4,-1])
    pattern.append([-1,0,4])

    pattern.append([0,-1,4])
    pattern.append([[0,-2,2],[0,-1,2]])###A and B

    pattern.append([-1,0,4])##prep_by

    pattern.append([0,-1,4])
    pattern.append([0,-1,4])####
        
    
    rule3flag=0
    for j in range(len(rules)):
        c=0
        mode=0
        t=c
        while (c<len(path) and t<len(rules[j]) and mode==0):

            if type(rules[j][t]) is tuple:                
                mode=2
                
                insideindex=0

                while (insideindex<len(rules[j][t]) and c+insideindex<len(path) and mode==2):

                    if type(rules[j][t][insideindex]) is list and path[c+insideindex] not in rules[j][t][insideindex]:
                        mode==1
                        break
                    if type(rules[j][t][insideindex]) is str and path[c+insideindex] != rules[j][t][insideindex]:
                        mode=1
                        break
                    insideindex+=1
                
            if mode==2:
                rule3flag=1
                t+=1
                c+=insideindex
                mode=0
                continue
            
            mode=0


            if type(rules[j][t]) is list and path[c] not in rules[j][t]:

                mode=1
                break
    
                mode=1
                break
            if type(rules[j][t]) is str and path[c] != rules[j][t]:

                mode=1
                break
            c+=1
            t+=1
        if mode==0:
     
            if c==len(path) and t==len(rules[j]):
                if rule3flag==0:
                    le=path[pattern[j][0]]
                    ri=path[pattern[j][1]]
                    if type(pattern[j][2]) ==str:
                        re=pattern[j][2]
                    else:
                        re=path[pattern[j][2]][0]
                    return [[le,ri,re]]
                else:
#                    print "!!!"
                    answer=[]
                    for i in range(len(pattern[j])):
                        le=path[pattern[j][i][0]]
                        ri=path[pattern[j][i][1]]
                        if type(pattern[j][i][2]) ==str:
                            re=pattern[j][i][2]
                        else:
                            re=path[pattern[j][i][2]][0]
                        answer.append([le,ri,re])
                    return answer
        
    
    return []
                   
                     
############################################################################
#                    extract sentences
############################################################################
path = "5.txt"
f = open(path)
line = f.readline()

while line:
    line = line.rstrip('\n')
    paragraph.append(line)
 #   sentence=line.replace('."','."#')
  #  sentence=line.replace('.','.#')
    sentence = line.replace('.','.#').replace('?','?#').replace('!','!#').replace('\xe2\x80\x94',' \xe2\x80\x94 ')
    sentence = sentence.split('#')
    for i in sentence:
        sentences.append(i.lstrip(' '))
    line = f.readline()
f.close()

while '' in sentences:
    sentences.remove('')
while '"' in sentences:
    sentences.remove('"')


path = "god_names_30.txt"
f = open(path)
line = f.read()
#line = line.replace(',',', ')
god_names = line.split(', ')
for i in god_names:
    if i.split(',')[0] != i:
        god_names.remove(i)
        god_names.append(i.split(',')[0])
        god_names.append(i.split(',')[1])


family_relation = ['bride','niece','greatgrandfather','greatgrandmother','greatgrandson','greatgrandsons','greatgranddaughter','greatgranddaughters','greatgrandchild','greatgrandchildren','father','mother','parent','parents','son','sons','daughter','daughters','husband','wife','brother','brothers','sisters','sister','grandmother','grandgrandfather','granddaughter','granddaughters','grandson','grandsons','grandchild','grandchildren','aunt','uncle','descendent','ancestor']
s_contain_name = set()
s_contain_relation = set()
person_name_in_corpus = set()
for i in range(len(sentences)):
    current_sentence = sentences[i]
    current_sentence = current_sentence.replace(', ',',')
    current_sentence = current_sentence.replace(',',' , ')
    current_sentence = current_sentence.replace('" ','"')
    current_sentence = current_sentence.replace(' "','"')
    current_sentence = current_sentence.replace('"',' " ')
    current_sentence = current_sentence.replace('\' ','\'')
    current_sentence = current_sentence.replace(' \'','\'')
    current_sentence = current_sentence.replace('\'',' \' ')
    current_sentence = current_sentence.replace('\' s',' \'s')
    current_sentence = current_sentence.replace('.',' .')
    current_sentence = current_sentence.replace('?',' ?')
    current_sentence = current_sentence.replace('!',' !')
    tokens = current_sentence.split(' ')
    for k in range(1,len(tokens)):
        if len(tokens[k])>1:
            if tokens[k][0] == tokens[k][0].upper():
                #print tokens[k]
                if (tokens[k][0]+tokens[k][1:].lower()) not in god_names:
                    person_name_in_corpus.add(tokens[k][0]+tokens[k][1:].lower())
   
    for j in tokens:
        if j.lower() in family_relation:
   
            s_contain_relation.add(i)
            break
    for j in tokens:
        if len(j)>1:
            if (j[0]+j[1:].lower()) in god_names:
                s_contain_name.add(i)
                break


intersection_result = list(s_contain_name & s_contain_relation)
intersection_result.sort()

union_result = list(s_contain_name | s_contain_relation)
union_result.sort()
c=0
extractedsentences=[]
path="mysmalltest"
f=open(path,'w')
 

f.write("<DOC>\n")
f.write("<TEXT>\n")


for i in range(len(sentences)):
    if c>=len(union_result):
        break
    if i==union_result[c]:
        sentence=sentences[i]
        if (sentence[-1]=="." or sentence[-1]=="!" or sentence[-1]=="?"):  
            extractedsentences.append(union_result[c])
            if sentence[0]=='"':
                temp=sentence[0]+sentence[1:].strip()
            
                temp=temp[0]+temp[1].upper()+temp[2:]

                f.write(temp+"\n")
            else:
                f.write(sentence[0].upper()+sentence[1:]+"\n")
                
            #print sentences[i] ##need a write operation to file 'my small test'
        c+=1


f.write("</TEXT>\n")
f.write("</DOC>\n")
f.close()
###############################################################################
#     Set up coreference list
###############################################################################
coreferenceSet = []
path = "5co.txt"
f = open(path)
line = f.readline()
while line:
    line = line.rstrip('\n')
    if line != 'Coreference set:':
        line = line.split('->')
        temp = []
        mid = []
        mid = line[1].split(",")
        num = int(mid[1]) - int(mid[2].replace("[", ""))
        coreference = []
        temp.append(line[1].split("\"")[1])
        temp.append(line[0].strip().replace("(", "").replace(")", "").split(',').pop(0))
        temp.append(line[0].strip().replace("(", "").replace(")", "").split(',').pop(1))
        coreference.append(temp)
        coreference.append(line[2].strip().replace("\"", "").split(" ")[num])
        coreferenceSet.append(coreference)
       
    line = f.readline()
f.close()
coref_list = []
for co in coreferenceSet:
    s1 = co[0][0][0].capitalize() + co[0][0][1:].lower()
    
    s2 = co[1][0].capitalize() + co[1][1:].lower()
    if s2 in god_names and s1 not in god_names:
        temp2 = []
        temp2.append(co[0][0])
        temp2.append(int(co[0][1]))
        temp2.append(int(co[0][2]))
        line2 = []
  
        line2.append(temp2)
        line2.append(co[1])
        coref_list.append(line2)

coreference=coref_list


###############################################################################
#     After getting output from jet, extract paths and do pattern matching(with
#      the help of coreference list)
###############################################################################
f=open("output","r")
a=f.readlines()
mode=0
b=""
l=[]
for line in a:
    if mode==1 and "--------" in line:
        
        mode=0
        l.append(b)
        b=""
    elif mode==1:
        
        b+=line
        
    elif mode==0 and "----Final dependency structure:" in line:
        
        mode=1

S=[]    
setList=[]
r=0
for x in l:
    x=x.strip('{}')
    ss=x.split("\n")
    setList=[]
    for line in ss:
        sss=line.strip().split(" ")
        if (len(sss)>1):
            sss[1]=int(sss[1].strip('()'))
            sss[4]=int(sss[4].strip('()'))
            t1=(sss[0],sss[1])
            t2=(sss[3],sss[4])
            t=[t1,sss[2],t2]
 
            setList.append(t)
    S.append(setList)
    r+=1


people=['he','she','his','her','whose','Whose','His','Her','He','Her']+god_names

links=[]

member=[]



#print sentences[extractedsentences[25]],S[25]
final=[]
for o in  range(len(S)):
    member=[]
    for i in range(len(S)):
        if i==o:
            for element in S[i]:
                       
                if element[0][0] in people and element[0] not in member:
                    member.append(element[0])
                    
                if element[2][0] in people and element[2] not in member:
                    member.append(element[2])

                if element[0][0].lower() in family_relation and element[0] not in member:
               
                    member.append(element[0])

                if element[2][0].lower() in family_relation and element[2] not in member:

                    member.append(element[2])

                if element[0][0][0]+element[0][0][1:].lower() in people and element[0] not in member:
                    member.append(element[0])

                if element[2][0][0]+element[2][0][1:].lower() in people and element[2] not in member:

                    member.append(element[2])
            test_list=S[i]###########new critical line

            tokens_in_s = set()
            for to in test_list:
                tokens_in_s.add(to[0])
                tokens_in_s.add(to[2])#抓取tokens_in_s#

            tokens_in_s=list(tokens_in_s)
            tokens_in_s.sort(lambda x,y: cmp(x[1],y[1]))
            
#            print sentences[extractedsentences[i]]
            root=build_tree(S[i])
            
            sentence=sentences[extractedsentences[i]]
#            print sentence,S[i]
            current_sentence = sentence
            current_sentence = current_sentence.replace(', ',',')
            current_sentence = current_sentence.replace(',',' , ')
            current_sentence = current_sentence.replace('" ','"')
            current_sentence = current_sentence.replace(' "','"')
            current_sentence = current_sentence.replace('"',' " ')              
            current_sentence = current_sentence.replace(' \'','\'')
            current_sentence = current_sentence.replace('\'',' \' ')
            current_sentence = current_sentence.replace('\' s',' \'s')
            current_sentence = current_sentence.replace('.',' .')
            current_sentence = current_sentence.replace('?',' ?')
            current_sentence = current_sentence.replace('!',' !')
            tokens_of_sentence = current_sentence.split(' ')

            for a in member:
                for b in member:

                    if a!=b:
                        result=find_path(a,b, S[i], root)
                        if len(result)>1:
                            ########new critical line

                            relation=patternMatch(result)
                                                       
                            
                            
                            
                            if len(relation)>0:
 #
                                person_o=['his','her','His','Her','Your','Their','My','whose','your','their','my','its','Its']
                                person_s= ['he','she','She','He','I','Me','me','You','you','They','they','him','her','who','Who','it','Its','whom','Whom']

                                for r in relation:
                                    appearance_for_person1 = []
                                    appearance_for_person2 = []
                                    relation_coref = [r[0][0],r[1][0],r[2]]
                                    for tok in tokens_in_s:
                                        if tok[0] ==r[0][0]:
                                            appearance_for_person1.append(tok)
                                        if tok[0] == r[1][0]:
                                            appearance_for_person2.append(tok)

                                    index_of_person1 = appearance_for_person1.index(r[0])
                                    index_of_person2 = appearance_for_person2.index(r[1])

                                    loc = -1
                                   # print relation,r[0][0],tokens_of_sentence[(loc+1):]
                                    for j in range(index_of_person1+1):
      
                                        loc = tokens_of_sentence[(loc+1):].index(r[0][0])
   
                                    person1_loc = [r[0][0],loc+1]

                                    for j in coreference:
                                        
                                        if j[0][0] == person1_loc[0] and j[0][2]==person1_loc[1] and j[0][1]==extractedsentences[i]+1:###tuple:string,token number
 #                                           print extractedsentences[i]+1,j[0][1],tokens_of_sentence
                                            relation_coref[0] = j[1]

                                    loc = -1
                                    for j in range(index_of_person2+1):
                                       
                                        loc = tokens_of_sentence[(loc+1):].index(r[1][0])
                                    
                                    person2_loc = [r[1][0],loc+1]

                                    for j in coreference:
                                        
                                        if j[0][0] == person2_loc[0] and j[0][2]==person2_loc[1] and j[0][1]==extractedsentences[i]+1:
#                                            print extractedsentences[i]+1,j[0][1],tokens_of_sentence
                                            relation_coref[1]=j[1]
                                    if relation_coref[0] in person_s or relation_coref[0] in person_o and relation_coref[1] in person_s or relation_coref[1] in person_o:
                                        print relation_coref,"coreference failure"

                                        
                                    else:
                                        final.append(relation_coref)



print final











    
    



        
