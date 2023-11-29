import enum
from math import e
from pydoc import classname
#from sys import exception
from symbol import typelist
import ply.yacc as yacc
import Decaf_parser as Parser
from Decaf_parser import Node
import re
import copy
class AST:
    def __init__(self):
        self.tree = None
        self.methodID = 1
        self.fieldID = 1
        self.fieldMap = {}
        self.constructorID = 1
        self.classLst = []
        self.canDeclareVars = 1
        self.oldMap = {}
        self.varIDTracker= 0
        self.thisClass= ""
        self.typeLst =[]
        self.AssignLst = []
        self.operationLst = []
        self.lineNo = 1
        self.supers = {}
        self.thisMethod= ""
        self.methodMap = {}
        self.methodParams = []
        self.methodNameRef = ""
        self.creatingNewObject=0
    def build(self, data):
        self.tree = data
    def remove_duplicates(self, array):
        seen = set()
        result = []
        for item in array:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    def extractNodesFromList(self,node):
        res = []
        orig = node
        exists = 0
        while(node.children): 
            for child in node.children:
                res.append(child)
            
            node= node.children[1]
        res = self.remove_duplicates(res)
        
        res[:] = [node for node in res if node.type not in ['class_body_decl_cont', 'class_decl_list']]
        node = orig
        return res
    def extractNodesFromFields(self,orig):
        res = []
        org= orig
        node = orig
        firstPass = 1
        while(node.children):
            if(firstPass):
                node= node.children[1]
                firstPass = 0
                continue     
            for child in node.children:
                res.append(child)
            node= node.children[1]
        res = self.remove_duplicates(res)
        res[:] = [node for node in res if node.leaf is not None]
        res[:] = [node for node in res if node.type not in ['variables_cont']]

        orig = org
        return res
    def extractNodesFromFormals(self,orig):
        #print(orig.children[0].children[0].children[1].leaf)
        res = []
        org= orig
        node = orig
        node = node.children[0]
        while(node.children):
            for child in node.children:
                res.append(child)
            node= node.children[1]

        res = self.remove_duplicates(res)
        res[:] = [node for node in res if node is not None]
        res[:] = [node for node in res if node.type not in ['formals_cont']]


        orig = org
        return res
    def extractStatementsFromBlock(self,orig):
        #print(orig.children[0].children[0].children[1].leaf)
        res = []
        org= orig
        node = orig
        node = node.children[0].children[0]
        while(node.children):
            for child in node.children:
                res.append(child)
            node= node.children[1]

        res = self.remove_duplicates(res)


        res[:] = [node for node in res if node is not None]
        res[:] = [node for node in res if node.type not in ['stmt_list']]

        
        orig = org
        return res 
    def extractAllBlockFromBlock(self,orig):
        #print(orig.children[0].children[0].children[1].leaf)
        res = []
        org= orig
        node = orig
        node = node.children[0].children[0]
        while(node.children):
            for child in node.children:
                res.append(child)
            node= node.children[1]

        res = self.remove_duplicates(res)

        
        res[:] = [node for node in res if node is not None]
        res[:] = [node for node in res if node.type not in ['stmt_list']]
        for i in res:
            if i.type == 'block':
                res.extend(self.extractAllBlockFromBlock(i))
        orig = org
        return res 
    def extractNodesFromVars(self,orig):
        res = []
        org= orig
        node = orig
        node=node.children[0]
        while(node.children):
            for child in node.children:
                    #print(child.leaf)
                    res.append(child)
            node= node.children[1]
        res = self.remove_duplicates(res)
        res[:] = [node for node in res if node.type not in ['variables_cont']]
        res[:] = [node for node in res if node.leaf is not None]
        orig = org        
        return res
    def extractNamesFromClassNodeLst(self,nodes):
        ret = []
        for node in nodes:
            ret.append(node.children[0].leaf)
        return ret
    def extractLineNoFromClassNodeLst(self,nodes):
        ret = []
        for node in nodes:
            ret.append(node.children[0].lineNo)
        return ret
    def extractNodesFromArgs(self,orig):
        res = []
        org= orig
        node = orig
        if not node.children:
            return []

        #node=node.children[0]

        while(node.children):
            for child in node.children:
                    #print(child.leaf)
                    res.append(child)
            if len(node.children) > 1:
                node= node.children[1]
            else:
                #node = node.children[0]
                break
        res = self.remove_duplicates(res)
        res[:] = [node for node in res if node.type not in ['arguments_cont']]
        #res[:] = [node for node in res if node.leaf is not None]
        orig = org       
        return res
    def remove_extra_commas(self,text):
        return text.replace(', ,', ',')
    def find_duplicate_line_numbers(self,lstNums):
        class_to_line = {}
        duplicate_line_numbers = []

        for class_name, line_num in zip(self.classLst, lstNums):
            if class_name in class_to_line:
                duplicate_line_numbers.append(line_num)
            else:
                class_to_line[class_name] = line_num

        return duplicate_line_numbers
    def find_class_name(self, lineNo, lstNums):
        class_to_line = dict(zip(self.classLst, lstNums))
        line_to_class = {v: k for k, v in class_to_line.items()}
        return line_to_class.get(lineNo, "Class name not found")
    def check_duplicate_fields(self):
        for i in range(1, len(self.fieldMap)+1):
            for j in range(i+1, len(self.fieldMap)+1):
                if (self.fieldMap[i][2] == self.fieldMap[j][2] and
                    self.fieldMap[i][3] == self.fieldMap[j][3]):
                    raise Exception(f"Duplicate field name {self.fieldMap[i][2]} found in class {self.fieldMap[i][3]} found at Line {self.fieldMap[j][4].lineNo}") 
    def print_tree(self, node):
        if isinstance(node, Node):
            if node.type == "program":
                classlst =  node.children[0]
                classlst = self.extractNodesFromList(classlst)
                self.classLst=self.extractNamesFromClassNodeLst(classlst)
                lstNums= self.extractLineNoFromClassNodeLst(classlst)
                findDups = self.find_duplicate_line_numbers(lstNums)
                if len(findDups)>0:
                    raise Exception(f"ERROR: CLASS '{self.find_class_name(findDups[-1],lstNums)}' ALREADY EXISTS. (LINE: '{findDups[-1]}')")
                for classNode in classlst:
                    class_name = ""
                    if classNode.type == 'class_decl':
                        class_name = classNode.children[0].leaf
                        print("Class Name: " + class_name)
                        decl_list = Node(type= "None") 
                        if len(classNode.children) > 2 and classNode.children[1].type == 'EXTENDS':
                            superclass_name = classNode.children[1].children[0].leaf
                            print("Superclass Name: " + superclass_name)
                            self.supers[class_name] = superclass_name
                            decl_list= classNode.children[2]
                        else:
                            print("Superclass Name:")
                            decl_list= classNode.children[1]
                        decl_list = self.extractNodesFromList(decl_list)
                        
                        for i in range(len(decl_list)):
                            decl_list[i]= decl_list[i].children

                        print("Fields:")
                        for child in decl_list:
                            
                            if child.type == 'field_decl':
                                field = child
                                fields = self.extractNodesFromFields(field.children[1])
                                for i in range(len(fields)):
                                    x = ""
                                    if (field.children[0].leaf == "" or field.children[0].leaf is None):
                                        x =f"FIELD: {self.fieldID}, {fields[i].leaf}, {class_name}, {field.children[1].children[0].leaf}"                             
                                    else:
                                        x =f"FIELD: {self.fieldID}, {fields[i].leaf}, {class_name}, {field.children[0].leaf}, {field.children[1].children[0].leaf}"
                                    x = self.remove_extra_commas(x)
                                    print(x)
                                     #ID, Type, Name, ref
                                    self.fieldMap[self.fieldID]= [self.fieldID,field.children[1].children[0].leaf,fields[i].leaf,class_name,fields[i]]
                                    self.check_duplicate_fields()
                                    self.fieldID +=1


                        print("Constructors:")
                        didPrintConst = 0
                        for child in decl_list:
                            varMap = {}
                            if child.type == 'constructor_decl':
                                varID = 1
                                didPrintConst = 1
                                method = child
                                prnt = f"CONSTRUCTOR: {self.constructorID}, {method.children[0].leaf}"
                                prnt = re.sub(", instance", "", prnt)
                                prnt = prnt.rstrip() 
                                if prnt[-1] == ',':
                                    prnt = prnt[:-1]   
                                print(prnt)
                                self.constructorID+=1
                                print("Constructor Parameters: ", end = "")

                                params = self.extractNodesFromFormals(method.children[2])

                                
                                if len(params) == 0:
                                    print("")
                                tempMap = {}
                                paramsLst= []
                                
                                for i in range(len(params)):
                                    if i != len(params) -1:
                                        
                                        print(str(varID) + ", ", end = "")
                                    else: 
                                        print(str(varID))
                                                            #ID, Type, Name, ref
                                    if params[i].children[1] not in varMap:
                                        varMap[params[i].children[1]] = [varID,params[i].children[0].leaf,params[i].children[1].leaf,params[i].children[1],True,classNode.children[0].leaf]
                                        #self.check_duplicate_vars(varMap)
                                        tempMap[params[i].children[1]] = [varID,params[i].children[0].leaf,params[i].children[1].leaf,params[i].children[1],True,classNode.children[0].leaf]
                                        varID +=1
                                    paramsLst.append(("constructor",params[i].children[0].leaf,class_name,method.children[0].leaf.split(", ")[0],method.children[0].leaf.split(", ")[1]))
                                if len(paramsLst) == 0:
                                    paramsLst.append(("constructor","NoParams",class_name,method.children[0].leaf.split(", ")[0],method.children[0].leaf.split(", ")[1],("User("+str(class_name)+")")))
                                self.methodParams.append(paramsLst)
                                block = self.extractStatementsFromBlock(method.children[3])
                                temp2= self.extractStatementsFromBlock(method.children[3])

                                print("Variable Table: ")
                                for i in tempMap.values():
                                                    ## ID     Name    instance/static   Type 
                                    print(f'VARIABLE {i[0]}, {i[2]}, formal, {i[1]}')
                                temp = block
                                # Get the index of 'block' in 'temp'
                                temp = self.block_iterate(temp,block,0)
                                block = temp
                                for i in block:
                                    if i.type == 'var_decl':
                                        nodes = self.extractNodesFromVars(i)
                                        last_type = None
                                        new_nodes = []
                                        for node in nodes:
                                                if node.type == 'type':
                                                    last_type = node
                                                elif node.type == 'variable' and new_nodes and new_nodes[-1].type == 'variable':
                                                    # Insert a new type node before this variable
                                                    new_type_node = Node('type', leaf=last_type.leaf)
                                                    new_nodes.append(new_type_node)
                                                new_nodes.append(node)
                                        nodes = new_nodes
                                        for i in range(len(nodes)):
                                            if nodes[i].type != 'type':
                                                continue
                                            if nodes[i+1] not in varMap:                    #ID, Type, Name
                                                varMap[nodes[i+1]]= [varID,nodes[i].leaf,nodes[i+1].leaf,nodes[i+1],False,classNode.children[0].leaf]
                                                #self.check_duplicate_vars(varMap)
                                                print(f'VARIABLE {varID}, {nodes[i+1].leaf}, local, {nodes[i].leaf}')
                                            
                                                varID+=1
                                print("Constructor Body: ", end = "")
                                self.printBlock(temp2,varMap,class_name)
                        if didPrintConst == 0:
                            print("Constructor Parameters:")
                            print("Variable Table:")
                            print("Constructor Body: ")
                        didMethod = 0
                        print("Methods: ")
                        for child in decl_list:
                            if child.type == 'method_decl':
                                varMap= {}
                                didMethod=1
                                method = child
                                pr= ""
                                retType = ""
                                methodName = method.children[2].leaf
                                tempInstance= method.children[0].leaf
                                
                                if (method.children[1].leaf != "void"):
                                    retType = method.children[1].children[0].leaf
                                    pr =(f"METHOD: {self.methodID}, {method.children[2].leaf}, {class_name}, {method.children[0].leaf}, {retType}")
                                else:
                                    retType = "void"
                                    pr =(f"METHOD: {self.methodID}, {method.children[2].leaf}, {class_name}, {method.children[0].leaf}")
                                self.methodMap[(class_name+str(self.methodID))]= [self.methodID,class_name,method,method.children[0].lineNo,retType,method.children[0].leaf.split(", ")[0],method.children[0].leaf.split(", ")[1]]
                                ##print("\n"+str(method.children[0].lineNo)+"\n")
                                pr = pr.rstrip() 
                                if pr[-1] == ',':
                                    pr = pr[:-1]
                                pr=self.remove_extra_commas(pr)    
                                print(pr)
                                self.methodID+=1
                                print("Method Parameters: ", end = "")

                                params = self.extractNodesFromFormals(method.children[3])

                                varID = 1
                                if len(params) == 0:
                                    print("")
                                tempMap = {}
                                paramsLst= []
                                tempInstance= tempInstance.split(", ")
                                for i in range(len(params)):
                                    if i != len(params) -1:
                                        print(str(varID) + ", ", end = "")
                                    else: 
                                        print(str(varID))
                                                    #ID, Type, Name
                                    if params[i].children[1] not in varMap:
                                        varMap[params[i].children[1]] = [varID,params[i].children[0].leaf,params[i].children[1].leaf,params[i].children[1],True,classNode.children[0].leaf]
                                        #print(params[i].children[1])
                                        #self.check_duplicate_vars(varMap)
                                        tempMap[params[i].children[1]] = [varID,params[i].children[0].leaf,params[i].children[1].leaf,params[i].children[1],True,classNode.children[0].leaf]
                                        #print(tempMap[params[i].children[1]])
                                        
                                        
                                        
                                        paramsLst.append((methodName,params[i].children[0].leaf,class_name,tempInstance[0],tempInstance[1],retType))

                                        varID +=1
                                if len(paramsLst )== 0:
                                    paramsLst.append((methodName,"NoParams",class_name,tempInstance[0],tempInstance[1],retType))
                                self.methodParams.append(paramsLst)
                                block = self.extractStatementsFromBlock(method.children[4])
                                temp2= self.extractStatementsFromBlock(method.children[4])

                                print("Variable Table: ")
                                for i in tempMap.values():
                                                    ## ID     Name    instance/static   Type  , printing formals here
                                    print(f'VARIABLE {i[0]}, {i[2]}, formal, {i[1]}')
                                    
                                temp = block
                                # Get the index of 'block' in 'temp'

                                temp = self.block_iterate(temp,block,0)
                                # Iterate over 'block'

                                    
                                block = temp
                                for i in block:
                                    
                                    if i.type == 'var_decl':
                                        
                                        nodes = self.extractNodesFromVars(i)
                                        last_type = None
                                        new_nodes = []
                                        for node in nodes:
                                                if node.type == 'type':
                                                    last_type = node
                                                elif node.type == 'variable' and new_nodes and new_nodes[-1].type == 'variable':
                                                    # Insert a new type node before this variable
                                                    new_type_node = Node('type', leaf=last_type.leaf)
                                                    new_nodes.append(new_type_node)
                                                new_nodes.append(node)
                                        nodes = new_nodes
                                        for i in range(len(nodes)):
                                            if nodes[i].type != 'type':
                                                continue

                                                                #ID, Type, Name
                                            if nodes[i+1] not in varMap:
                                                varMap[nodes[i+1]]= [varID,nodes[i].leaf,nodes[i+1].leaf,nodes[i+1],False,classNode.children[0].leaf]
                                            #print(nodes[i+1])
                                            #self.check_duplicate_vars(varMap)
                                                print(f'VARIABLE {varID}, {nodes[i+1].leaf}, local, {nodes[i].leaf}')
                                            
                                                varID+=1        
                                print("Method Body:",end = "")
                                self.printBlock(temp2,varMap,classNode.children[0].leaf)
                        if didMethod == 0:
                            print("Method Parameters:")
                            print("Variable Table:")
                            print("Method Body:")
                        # Add code here to print methods

                    print("-------")
        else:
            print((node) + " not instance\n")
    def check_duplicate_vars(self, varMap):
        seen = {}
        for key, value in varMap.items():
            if value[2] in seen:  # Compare the variable names
                raise Exception(f"ERROR: Duplicate variable name {value[2]} found at line {value[5].lineNo} and line {seen[value[2]].lineNo}")
            seen[value[2]] = value[5]  # Store the node object for later reference
    def block_iterate(self,temp,block,block_index):
                for i,block in enumerate(block):
                        if block.type == 'block':
                            block_index=i
                            for j in self.extractAllBlockFromBlock(block):
                                            
                                                # Insert 'j' into 'temp' at the index after 'block'
                                temp.insert(block_index + 1, j)
                                                # Increment the index for the next insertion
                                block_index += 1
                        if block.type == "if_else":
                            block_index = i
                            if block.children[1].type == "block":
                                
                                t =self.extractAllBlockFromBlock(block.children[1])
                                for j in t:
                                                
                                                    # Insert 'j' into 'temp' at the index after 'block'
                                    temp.insert(block_index + 1, j)
                                                        # Increment the index for the next insertion
                                    block_index += 1
                               
                            if block.children[2].type == "block":
                                t =self.extractAllBlockFromBlock(block.children[2])
                                for j in t:
                                                
                                                    # Insert 'j' into 'temp' at the index after 'block'
                                    temp.insert(block_index + 1, j)
                                                        # Increment the index for the next insertion
                                    block_index += 1
                               
                                                                                        
                            
                        if block.type == "if" or block.type == "while":
                            if block.children[1].type == "block":
                                block_index = i
                                t =self.extractAllBlockFromBlock(block.children[1])
                                for j in t:
                                                
                                                    # Insert 'j' into 'temp' at the index after 'block'
                                    temp.insert(block_index + 1, j)
                                                        # Increment the index for the next insertion
                                    block_index += 1
                               
                                
                        if block.type == "for":
                            if block.children[3].type == "block":
                                block_index = i
                                t =self.extractAllBlockFromBlock(block.children[1])
                                for j in t:
                                                
                                                    # Insert 'j' into 'temp' at the index after 'block'
                                    temp.insert(block_index + 1, j)
                                                        # Increment the index for the next insertion
                                    block_index += 1
                               
                                        
                return temp

    def printBlock(self,block,oldMap,className = "",recursive = 0):
        self.thisClass = className
        print("\nBlock([",end = "")
        ## redeclare varMap
        self.canDeclareVars = 1  
        newVarMap= {}
        #make Sure we mention 
        for i in block:
            ## neeed to construct variable map in this scope so that if we have duplicate vars it chooses the right one
            if i.type == "var_decl":
                    nodes = self.extractNodesFromVars(i)
                    last_type = None
                    new_nodes = []
                    for node in nodes:
                        if node.type == 'type':
                            last_type = node
                        elif node.type == 'variable' and new_nodes and new_nodes[-1].type == 'variable':
                            # Insert a new type node before this variable
                            new_type_node = Node('type', leaf=last_type.leaf)
                            new_nodes.append(new_type_node)
                        new_nodes.append(node)
                    nodes = new_nodes
                    for i in range(len(nodes)):
                        #if recursive == 1:
                            #oldMap[nodes[i]]= [nodes[i].children[0]]
                        if nodes[i].type != 'type' or i+1 >= len(nodes) :
                            #print("leaf : "+nodes[i].leaf + "\n\n")
                            #print(oldMap )
                            #print("\n\n\n\n\n")
                            continue                    #ID, Type, Name
                        
                        newVarMap[nodes[i+1]]= [oldMap[nodes[i+1]][0],nodes[i].leaf,nodes[i+1].leaf,False,className,nodes[i+1]]
        for i in oldMap:
            if oldMap[i][4] == True and recursive == 0:
                newVarMap[oldMap[i][3]]= [oldMap[i][0],oldMap[i][1],oldMap[i][2],True,className,oldMap[i][3]]
        
        ##print(newVarMap)
        self.oldMap = oldMap
        self.check_duplicate_vars(newVarMap)
        if len(block) == 0:
            print("Skip-stmt",end = "")
        for index,i in enumerate(block):
            self.printStatement(index,i,newVarMap,oldMap,block,className)
        print("\n])")

    def printStatement(self,index,i,newVarMap,oldMap,block,className = ""):
            #print("\n")
            self.lineNo = i.lineNo
            if i.type == "var_decl":
                err = 0
                lastLineNo = 0
                if(self.canDeclareVars == 0):
                    err = 1
                vars=self.extractNodesFromVars(i)
                for index, i in enumerate(vars):
                    if index == 0:
                        continue
                    lastLineNo =int(oldMap[i][3].lineNo)
                if err:
                    raise Exception (f"ERROR: Vars must be at top of block (Line {lastLineNo}) ")
                
            else:
                self.canDeclareVars =0
            if i.type == "if":
                print("If-stmt",end = "(")
                self.typeLst = ["boolean"]
                self.printExpression(i.children[0],newVarMap)
                self.simplifyLst(self.typeLst)
                print(",",end = "")
                self.printStatement(index,i.children[1],newVarMap,oldMap,block)
                print(",",end = "")
                print("Skip-stmt",end = "")
                print("",end = ")")                
            if i.type == "if_else":
                print("If-stmt",end = "(")
                self.typeLst = ["boolean"]
                self.printExpression(i.children[0],newVarMap)
                print(",",end = "")
                self.simplifyLst(self.typeLst)
                self.printStatement(index,i.children[1],newVarMap,oldMap,block)
                print(", Else(",end = "")
                self.printStatement(index,i.children[2],newVarMap,oldMap,block)
                print(")",end = ")")
            if i.type == "for_stmt":
                print("For-stmt(",end = "")
                if(i.children[0].children[0].type) == "empty":
                    print("Skip-stmt",end = "")
                    print(", ",end = "")
                else:
                    self.printStmtExpr(index,i.children[0],newVarMap,block)

                if(i.children[1].children[0].type) == "empty":
                    print("Skip-stmt",end = "")
                else:
                    self.typeLst = ["boolean"]
                    self.printExpression(i.children[1].children[0],newVarMap)
                    self.simplifyLst(self.typeLst)
                print(", ",end = "")
                if(i.children[2].children[0].type) == "empty":
                    print("Skip-stmt",end = "")
                else:
                    self.printStmtExpr(len(block)-1,i.children[2],newVarMap,block)
                print(", ")
                self.printStatement(index,i.children[3],newVarMap,oldMap,block)
                print(")",end = "")
            if i.type == "continue":
                print(" Continue-stmt")
            if i.type == "while":
                print("While-stmt",end = "(")
                self.typeLst = ["boolean"]
                self.printExpression(i.children[0],newVarMap)
                self.simplifyLst(self.typeLst) 
                print(",",end = "")
                self.printStatement(index,i.children[1],newVarMap,oldMap,block)
                print("",end = ")")
            if i.type == "break":
                print(" Break-stmt")
            if i.type == "block":
                recursiveCall = self.extractStatementsFromBlock(i)
                self.printBlock(recursiveCall,oldMap,self.thisClass,1)
            if i.type == "return_stmt":
                methodNode = self.findMethod(self.lineNo)
                #retType = methodNode[4]
                self.typeLst = [methodNode[4]]
                
                print("\nReturn-stmt(",end = "")   
                if(i.children[0].children[0].type == "empty"):
                    print("Skip-stmt",end = "")
                else:
                    self.printExpression(i.children[0].children[0],newVarMap,1)
                exceptionFlag =0
                res= ""
                try: 
                    res =self.simplifyLst(self.typeLst)
                except Exception as e:
                    #print("",e)
                    exceptionFlag=1
                if exceptionFlag == 1 or (self.isSubtypeOf(res,methodNode[4])==False):
                    raise Exception(f'Type error at line {i.lineNo}, return statement is formatted incorrectly')
                if len(self.typeLst) == 1:
                    raise Exception(f'Type error at line {i.lineNo}, missing info in return statement')
                
                print(")",end = "")
            if i.type == "stmt_expr":
                self.printStmtExpr(index,i,newVarMap,block)

    def findMethod(self, lineNo):
        max_i = None
        for key, element in self.methodMap.items():
            if int(element[3]) < lineNo:
                if max_i is None or int(element[3]) > int(max_i[3]):
                    max_i = element
        return max_i
            
    def printStmtExpr(self,index,i,newVarMap,block):
                print("\nStmt-Expr(",end = "")
                
                descend = (i.children[0]) ## Now from assign :
                ##print(descend.children[0].type)
                if (descend.children[0].leaf == "method_invocation" or descend.children[0].type == "method_invocation"):
                    
                    self.printMethod_invocation(descend.children[0],newVarMap)
                else:
                    self.printAssign(descend.children[0],newVarMap)
                     
                if (index == len(block)-1):
                    print(")",end = "")
                else:
                    print(")",end = ", ")
    def printLHS(self,lhs,varMap):
        field= lhs.children[0]
        self.printFieldAccess(field,varMap)
    def value_exists(self, var_map, value):
        for item in var_map:
            for key in var_map[item]:
                if isinstance(key, str):  # Check if the item is a dictionary
                    if key == value:
                        return item
        return None
    def printFieldAccess(self,field,varMap,isMethod=0):
        #print("\n\nHEREHERHEH\n\n\n")
        self.lineNo= field.children[0].lineNo
        if field.type == "id_field_access":
            item = self.value_exists(varMap,field.children[0].leaf)
            if item:
                #   if field.children[0].leaf in varMap.values():
                #print("Before, ",end = str(self.typeLst))
                self.typeLst.append(varMap[item][1])
                #print("Appending :",end = "")
                #print(self.typeLst)
                #print("\n\nHERE\n\n")
                print("Variable("+str(varMap[item][0])+")",end = "")
            else:
                ## HERE WE DO ERROR TESTING
                
                if field.children[0].leaf in self.classLst:
                    print("Class-Reference("+field.children[0].leaf+")",end = "")
                    self.typeLst.append("class-literal("+ field.children[0].leaf+ ")")
                else:
                    errFlag= 1
                    for i in self.oldMap:
                        if field.children[0].leaf == self.oldMap[i][2] and (field.children[0].lineNo > self.oldMap[i][3].lineNo):
                            errFlag =0
                            print("Variable("+str(self.oldMap[i][0])+")",end = "")
                            self.typeLst.append(self.oldMap[i][1])
                            break
                    if errFlag:
                        raise Exception(f"ERROR: Cannot resolve reference for variable {field.children[0].leaf} at line {field.children[0].lineNo}")
            #elif field.children[0].leaf in self.fieldMap:
            #    print("Field-Access("+str(self.fieldMap[field.children[0].leaf][0])+", "+ str(self.fieldMap[field.children[0].leaf][2])+ ")",end = "")
        else:
            
            ## primary DOT ID
            ## primary is field.children[0], ID is field.children[1]
            inClass = 0
            fieldflag = 0
            if(isMethod == 1):
                try:
                    base = field.children[0].children[0].children[0].children[0].leaf
                    
                    #if base == "this":
                    #    base = self.thisClass
                    #if base == "super":
                    #    base == self.supers[self.thisClass]
                    if base in self.classLst:
                        inClass = 1
                        
                        print("Method-call-expression(Class-Reference-expression("+ base+")", end="")
                    else:
                        print("Method-call-expression(", end="")
                except (IndexError, AttributeError):
                    print("Method-call-expression(", end="")
                
            else:
                print("Field-Access(",end = "")
                fieldflag = 1
            if inClass == 0:
                (self.printPrimary(field.children[0],varMap))
            print(", ",end = "")
            print(field.children[1].leaf ,end = "")
            self.methodNameRef= field.children[1].leaf
            if fieldflag ==1:
                className = ""
                try:
                    className = field.children[0].children[0].children[0].children[0].leaf
                except Exception as e:
                    className=(self.thisClass)
                if className not in self.classLst:
                    className= self.thisClass    
                id = self.findFieldID(field.children[1],className)
                if id == None:
                    if self.thisClass in self.supers.keys():
                        id = self.findFieldID(field.children[1],self.supers[self.thisClass])
                    if id == None:
                        raise Exception(f"Cannot resolve field access at line {self.lineNo}")
                print(", "+ str(id),end = "")
            if isMethod==0:
                print(")",end ="")
    def findFieldID(self, given_node,class_name):
        #print(class_name)
        for i in self.fieldMap:
            if self.fieldMap[i][2] == given_node.leaf and self.fieldMap[i][3] == class_name:
                return self.fieldMap[i][0]
        return None
    def modify_string(self,s):
        s = s[:-5]
        s = s.capitalize()
        return s
    def printExpression(self,expression,varMap,recursive = 0):
        ## still print yet return "" so that it can be called in a print statement
        
        if recursive == 0:
            print("Expr(",end = "")
        
        if expression.leaf:
            if (expression.leaf == "primary"):
                self.printPrimary(expression.children[0],varMap)
            else:                        
                self.printAssign(expression.children[0],varMap)
        else:
            if len(expression.children) >1:
                print("Binary-Expression",end = "(")
                print(self.modify_string(expression.type),end = "")
                self.operationLst.append(self.modify_string(expression.type))
                print(", ",end = "")                
                self.printExpression(expression.children[0],varMap,recursive=1)
                print( ", ",end = "")
                self.printExpression(expression.children[1],varMap,recursive =1)
                print (")",end = "")
            else:
                if(expression.type == "not_expr"):
                    print("UnaryExpression(!,",end = "")
                    self.printExpression(expression.children[0],varMap,recursive=1)
                    self.operationLst.append("!")
                elif expression.type == "minus_expr":
                    print("UnaryExpression(-,",end = "")
                    self.operationLst.append("Unary-")
                    self.printExpression(expression.children[0],varMap,recursive=1)
                elif expression.type == "pos_expr":
                    self.operationLst.append("+")
                    print("UnaryExpression(+,",end = "")
                    self.printExpression(expression.children[0],varMap,recursive=1)                       
                else:
                    print(expression.type + "(",end = "")
                    self.printExpression(expression.children[0],varMap,recursive=1)
                
                print (")",end = "")
        if recursive == 0:
            print(")",end = "")
        return ""
    def printPrimary(self,primary,varMap): 
        if primary.type == "this":
            print("This", end = "")
            self.typeLst.append("user("+self.thisClass+")")
        elif primary.type == "super":
            print("Super", end = "")
            if self.thisClass not in self.supers:
                raise Exception(f"Type error at line {self.lineNo}, Super class does not exist")
            self.typeLst.append("user("+self.supers[self.thisClass]+")")
        elif primary.type == "lhs":
            self.printLHS(primary.children[0],varMap)
        elif primary.type == "method_invocation":
            self.printMethod_invocation(primary.children[0],varMap)
        elif primary.type == "paren_expr":
            self.printExpression(primary.children[0],varMap)
        elif primary.type == "new_object":
            ## TODO: print this for new object
            print("New-object-expression(", end = "")
            print(primary.children[0].leaf, end = "")
            
            self.typeLst.append("user("+primary.children[0].leaf+")")
            self.creatingNewObject = 1
            self.printArgs(primary.children[1],varMap)
            pass
        else:
            print("Constant-expression(",end = "")
            if (primary.children[0].type) =="Integer-constant":
                self.typeLst.append("int")
            elif (primary.children[0].type) =="Float-constant":
                self.typeLst.append("float")
            elif (primary.children[0].type) =="String-constant":
                self.typeLst.append("string")
            elif (primary.children[0].type) =="ConstantTrue":
                self.typeLst.append("boolean")
            elif (primary.children[0].type) =="ConstantFalse":
                self.typeLst.append("boolean")
            elif (primary.children[0].type) == "ConstantNull":
                self.typeLst.append("null")
            print(primary.children[0].type + "(",end = "")
            print(primary.children[0].children[0],end = ")")
            print(")",end = "")
        return ""
    def printMethod_invocation(self,primary,varMap):
        #print("!!!!"+primary.children[0].type+"!!!!")

        self.printFieldAccess(primary.children[0],varMap,isMethod=1)
        self.printArgs(primary.children[1],varMap)
        print(")",end = "")    
        ## still print yet return "" so that it can be called in a print statement
        return ""
    def printArgs(self,args,varMap):
        args1 = self.extractNodesFromArgs(args)
        print(", Arguments: [",end = "")
        intendedRetType = self.typeLst[-1]
        ClassName = ""
        if(len(intendedRetType)>4 and intendedRetType[:4] == "user"):
            start = intendedRetType.find("(") + 1 
            end = intendedRetType.find(")") 
            ClassName = intendedRetType[start:end]
        elif(len(intendedRetType)>10 and intendedRetType[:13] == "class-literal"):
            start = intendedRetType.find("(") + 1 
            end = intendedRetType.find(")") 
            ClassName = intendedRetType[start:end]
        if ClassName == "":
            ClassName = self.thisClass            
        copy_typeLst = self.typeLst[:-1]
   
        index = len(self.typeLst)
        deref=index
        argLst = []
        for i in range(len(self.methodParams)):
            for k in range(len(self.methodParams[i])):
                if self.creatingNewObject == 1 and self.methodParams[i][k][0] == "constructor" and self.methodParams[i][k][2] == ClassName:
                    argLst.append(self.methodParams[i][k])
                if self.methodParams[i][k][0] == self.methodNameRef and self.methodParams[i][k][2] == ClassName:
                    argLst.append(self.methodParams[i][k])

        argIndex = 0        
        for index, arg in enumerate(args1):
            testLst = []
            prevCutoff = len(self.typeLst[:])
            prevTypeLst = self.typeLst[:]
            prevOperationLst = self.operationLst[:]
            if len(argLst) > 0:
                testLst.append(argLst[argIndex][1])  
            self.printExpression(arg,varMap,1)
            if len(self.typeLst) == prevCutoff:
                pass
            else:
                testLst.append(self.typeLst[prevCutoff:])
                testLst = self.flatten(testLst)
                savingOperations= self.operationLst[:]
                self.operationLst = self.operationLst[len(prevOperationLst):]
                prevTypeLst.append(self.simplifyLst(testLst))
                self.typeLst = prevTypeLst
                self.operationLst = savingOperations
            if index != (len(args1)-1):
                print(", ", end = "")
            argIndex +=1

            copy_operationLst = self.operationLst[:]
        
        
        addedElements = self.typeLst[deref:]
        auxLst = []
        requiredParams = 0
        foundRetType = intendedRetType
        foundMethod = 0
        for i in range(len(self.methodParams)):
            for k in range(len(self.methodParams[i])):
                #print(self.methodNameRef)
                #print(ClassName)
                if self.creatingNewObject == 1: #and self.methodParams[i][k][0] == "constructor" and self.methodParams[i][k][2] == ClassName:
                    foundRetType = "user(" + ClassName + ")"
                    foundMethod = 1
                
                if self.methodParams[i][k][0] == self.methodNameRef and self.methodParams[i][k][2] == ClassName:
                    
                    foundMethod = 1
                    foundRetType = self.methodParams[i][k][5]
                    #print(self.methodParams[i][k])
                    
                    if(self.methodParams[i][k][1] != "NoParams"):
                        requiredParams+=1
        #print(self.typeLst)
        #print(requiredParams)          
        if requiredParams!= (len(self.typeLst)-deref):
            raise Exception(f"Invocation error at line {self.lineNo}, Number of parameters does not match up, or we cannot find which method signature you are referring to")
        if foundMethod == 0 :
            raise Exception(f"Invocation error at line {self.lineNo}, We cannot find which method signature you are referring to")
        #print(addedElements)
        copy_typeLst.append(foundRetType)
        
        self.typeLst= copy_typeLst
        #print(self.typeLst)
        print("]",end = "")
        self.creatingNewObject = 0
        self.methodNameRef = ""
    def printAssign(self,descend,newVarMap):
                self.typeLst = []
                if descend.type == "assign_expr":
                    
                    print("assign(", end = "")
                    self.printLHS(descend.children[0],newVarMap)
                    
                    print(", ", end = "")
                    self.printExpression(descend.children[1],newVarMap,recursive=1)
                    self.AssignLst.append(self.typeLst)
                    self.AssignLst=self.flatten(self.AssignLst)
                    #print(self.AssignLst)
                    print(", ",end = "")
                    #print(self.AssignLst)
                    #print(self.operationLst)
                    if len(self.AssignLst) == 1:
                        self.AssignLst.append(self.AssignLst[0])
                    else:
                        self.AssignLst[1]= self.simplifyLst(self.AssignLst)
                    print(self.AssignLst[0]+ ", " + self.AssignLst[1], end = "")
                    print(")", end = "")

                    self.operationLst= []
                    #print(self.typeLst)
                elif descend.type == "increment_assign_expr":
                    print("Auto-expression(", end = "")
                    self.printLHS(descend.children[0],newVarMap)
                    print(", ++, post",end = "")
                    print(")", end = "")
                    self.operationLst.append("++")
                    self.AssignLst.append(self.typeLst)
                    self.AssignLst=self.flatten(self.AssignLst)
                    if self.AssignLst[0] != "float" and self.AssignLst[0] != "int":
                        print(self.AssignLst)
                        raise Exception(f"Type error at line {self.lineNo}, incrementing needs a number")
                elif descend.type == "decrement_assign_expr":
                    self.operationLst.append("--")
                    print("Auto-expression(", end = "")
                    self.printLHS(descend.children[0],newVarMap)
                    print(", --, post",end = "")
                    print(")", end = "")
                    self.AssignLst.append(self.typeLst)
                    self.AssignLst=self.flatten(self.AssignLst)
                    if self.AssignLst[0] != "float" and self.AssignLst[0] != "int":
                        raise Exception(f"Type error at line {self.lineNo}, decrementing needs a number")
                elif descend.type == "pre_increment_assign_expr":
                    self.operationLst.append("++")
                    print("Auto-expression(", end = "")
                    self.printLHS(descend.children[0],newVarMap)
                    print(", ++, pre",end = "")
                    print(")", end = "")
                    self.AssignLst.append(self.typeLst)
                    self.AssignLst=self.flatten(self.AssignLst)
                    if self.AssignLst[0] != "float" and self.AssignLst[0] != "int":
                        raise Exception(f"Type error at line {self.lineNo}, incrementing needs a number")
                elif descend.type == "pre_decrement_assign_expr":
                    self.operationLst.append("--")
                    print("Auto-expression(", end = "")
                    self.printLHS(descend.children[0],newVarMap)
                    print(", --, pre",end = "")
                    print(")", end = "")
                    self.AssignLst.append(self.typeLst)
                    self.AssignLst=self.flatten(self.AssignLst)
                    if self.AssignLst[0] != "float" and self.AssignLst[0] != "int":
                        raise Exception(f"Type error at line {self.lineNo}, decrementing needs a number")
                self.typeLst = []
                self.AssignLst=[]
    def flatten(self, lst):
        flattened_list = []
        for sub_list in lst:
            if isinstance(sub_list, list):
                for item in sub_list:
                    flattened_list.append(item)
            else:
                flattened_list.append(sub_list)
        return flattened_list
    def isSubtypeOf(self,thing1,thing2):
        if thing1 == thing2:
            return True
        if thing1 == "int" and thing2 == "float":
            return True
        if (len(thing2)>4) and thing1 == "null" and thing2[:4] == "user":
            return True
        if (len(thing1) >4) and (len(thing2) >4) and (thing1[:4] =="user") and (thing2[:4]=="user") and (thing1.find("(") != -1) and (thing2.find("(")!= -1):
            start = thing1.find("(") + 1 
            end = thing1.find(")") 
            thingy1 = thing1[start:end] 
            start = thing2.find("(") + 1 
            end = thing2.find(")") 
            thingy2 = thing2[start:end]
            try:
                if (self.supers[thingy1] == thingy2):
                    return True
            except KeyError:
                return False
        if (len(thing1) >13) and (len(thing2) >13) and (thing1[:13] =="class-literal") and (thing2[:13]=="class-literal") and (thing1.find("(") != -1) and (thing2.find("(")!= -1):
            start = thing1.find("(") + 1 
            end = thing1.find(")") 
            thingy1 = thing1[start:end] 
            start = thing2.find("(") + 1 
            end = thing2.find(")") 
            thingy2 = thing2[start:end]
            try:
                if (self.supers[thingy1] == thingy2):
                    return True
            except KeyError:
                return False
        return False
    def simplifyLst(self,lst):
        intFlag = 0
        #print(lst)
        #if len(lst[1]) >4 and len(lst[1]) 
        if "void" in lst:
            for i in lst:
                if i != "void":
                    raise Exception(f"Type error at line {self.lineNo}, void must not have anything other than void existing")
        if "boolean" not in lst and "!" in self.operationLst:
            raise Exception(f"Type error at line {self.lineNo}, unary negation must be performed on booleans")
        if "int" not in lst and "float" not in lst and "Unary-" in self.operationLst:
            raise Exception(f"Type error at line {self.lineNo}, unary minus must be performed on numbers")
        if "int" in lst and not ("float" in lst):
            intFlag = 1
        if "float" in lst or "int" in lst:
            if "string" in lst:
                raise Exception(f"Type error at line {self.lineNo}, strings cannot interact with numbers")
            if "boolean" in lst:
                if lst[0] != "boolean":
                    raise Exception(f"Type error at line {self.lineNo}, assigning boolean to nonboolean var")
                for i in range(len(lst)):
                    if(lst[i]== "boolean" and i != 0):
                        raise Exception(f"Type error at line {self.lineNo}, cannot operate boolean variables with numbers")
                if ">" not in self.operationLst and ">=" not in self.operationLst and"<" not in self.operationLst and "<=" not in self.operationLst and "==" not in self.operationLst and "!=" not in self.operationLst:
                    raise Exception(f"Type error at line {self.lineNo}, cannot assign numbers to boolean")
                return "boolean"

            if intFlag:
                return "int"
            
            return "float"
        if "string" in lst:
            if len(self.operationLst)>0:
                raise Exception(f"Type error at line {self.lineNo}, Strings cannot perform operations")
            if "string" == lst[0]:
                for i in range(len(lst)):
                    if lst[i] != "string":
                        raise Exception(f"Type error at line {self.lineNo}, string not able to be involved in other operations other than assigning to another string")
            return "string"
        #if "boolean" == lst[0]:
            #if "||" in self.operationLst or "&&" in self.operationLst:
                #for i in range(len(lst)):
                    #if lst[i] != "boolean":
                        #raise Exception(f"Type error at line {self.lineNo}")
        if len(lst) > 1:
            return lst[1]
        else:
            return lst[0]            
if __name__ == "__main__":
    ast = AST()