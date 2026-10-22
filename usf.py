import json
import os
import requests
from playwright.sync_api import sync_playwright

# Target base graph ID
GRAPH_ID = "zyaymjbghu"

# Global state trackers
_graph_state = None
_expressions_by_id = {}
_expr_counter = 0  # Global sequencer tracking all appended elements

def set_key(a):
    global GRAPH_ID
    GRAPH_ID=a
def _init_graph():
    """Cleanly fetches and normalizes the base graph expressions list structure."""
    global _graph_state, _expressions_by_id
    if _graph_state is not None:
        return

    print(f"[*] Fetching baseline graph parameters: {GRAPH_ID}...")
    url = f"https://desmos.com/calculator/{GRAPH_ID}"
    response = requests.get(url, headers={"Accept": "application/json"})
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch base graph data. Status: {response.status_code}")

    _graph_state = response.json().get("state", {})
    
    # Guarantee state.expressions.list exists
    if "expressions" not in _graph_state:
        _graph_state["expressions"] = {"list": []}
    elif isinstance(_graph_state["expressions"], list):
        _graph_state["expressions"] = {"list": _graph_state["expressions"]}
    elif "list" not in _graph_state["expressions"]:
        _graph_state["expressions"]["list"] = []

    # Map existing items
    for expr in _graph_state["expressions"]["list"]:
        if isinstance(expr, dict) and "id" in expr:
            _expressions_by_id[expr["id"]] = expr


def append(a, foldername=None, is_note=False, action=None, button_label="Click", 
           colour="black", trans_bg=0.5, trans_lines=1, lines="False"):
    """Core backend injector equipped with color mapping and opacity controls."""
    global _expr_counter
    _init_graph()
    
    _expr_counter += 1
    expr_id = f"py_expr_{_expr_counter}"
    
    expr_payload = {
        "id": expr_id,
        "type": "text" if is_note else "expression",
    }
    
    if is_note:
        expr_payload["text"] = a
    else:
        expr_payload["latex"] = a
        
        # 1. Color mapping dictionary (Desmos native names vs Custom Hex values)
        color_map = {
            "red": "red",          # Desmos native
            "green": "green",      # Desmos native
            "black": "black",      # Desmos native
            "purple": "purple",    # Desmos native
            "blue": "#2d70b3",        # Desmos native
            "orange": "orange",    # Desmos native
            "gold": "#B8860B",
            "dark_green": "#006400",
            "crimson_red": "#660000"
        }
        
        # Normalize incoming text choice, fallback to raw input if user gives direct hex/rgb
        clean_colour = str(colour).lower().strip()
        expr_payload["color"] = color_map.get(clean_colour, colour)
        

        expr_payload["fillOpacity"] = str(float(trans_bg))
        expr_payload["lineOpacity"] = str(float(trans_lines))

        # 3. SAFE BORDER CONTROL FIX:
        # Instead of feeding 'lines' to a non-point expression, toggle the outline width thickness
        if str(lines).lower() == "false":
            expr_payload["lineWidth"] = str(0)
        else:
            expr_payload["lineWidth"] = str(2.5)  # Standard Desmos default line thickness

        # 4. Action button handling setup
        if action is not None:
            expr_payload["clickableInfo"] = {
                "enabled": True,
                "description": button_label,
                "latex": action
            }
    
    expr_list = _graph_state["expressions"]["list"]
    
    if foldername:
        folder_id = f"py_folder_{foldername.lower().replace(' ', '_')}"
        folder_exists = any(expr.get("id") == folder_id for expr in expr_list)
                
        if not folder_exists:
            folder_payload = {
                "id": folder_id,
                "type": "folder",
                "title": foldername,
                "collapsed": False
            }
            expr_list.append(folder_payload)
            _expressions_by_id[folder_id] = folder_payload
            
        expr_payload["folderId"] = folder_id

    expr_list.append(expr_payload)
    _expressions_by_id[expr_id] = expr_payload


def note(text_content, foldername=None):
    """Helper function to append a plain text note directly into the workspace."""
    append(text_content, foldername=foldername, is_note=True)


def search_var(var_name):
    """Searches if a variable assignment structure exists.
    
    If you pass 'a', it searches for 'a=' or 'a_1=' patterns, ignoring values.
    """
    _init_graph()
    clean_search = str(var_name).replace(" ", "") + "="
    
    for expr in _graph_state["expressions"]["list"]:
        if "latex" in expr and expr["latex"] is not None:
            clean_latex = expr["latex"].replace(" ", "")
            if clean_search in clean_latex:
                return True
    return False


def search_exp(exact_latex):
    """Searches for an exact, literal mathematical expression row match.
    
    If you input 'a=0', it returns True ONLY if the row reads exactly 'a=0'.
    """
    _init_graph()
    clean_search = str(exact_latex).replace(" ", "").replace("\\", "")
    
    for expr in _graph_state["expressions"]["list"]:
        if "latex" in expr and expr["latex"] is not None:
            clean_latex = expr["latex"].replace(" ", "").replace("\\", "")
            if clean_search == clean_latex:
                return True
    return False


def search_broad(name_to_check):
    """Comprehensive check covering assignments and function declarations.
    
    If the search target contains a subscript (e.g. 'a_{1}'), it hunts for that exact subscript.
    Otherwise, it avoids partial matches with subscript patterns.
    """
    _init_graph()
    clean_name = str(name_to_check).replace(" ", "")
    clean_name = clean_name.replace("{{", "{").replace("}}", "}")
    
    # 1. Base patterns required for variables or functions
    patterns = [
        clean_name + "=",
        clean_name + "\\left",
        clean_name + "("
    ]
    
    # 2. Only include general subscript tracking if the user explicitly searched for a subscript
    if "_{" in clean_name:
        patterns.append(clean_name)
    
    for expr in _graph_state["expressions"]["list"]:
        if "latex" in expr and expr["latex"] is not None:
            clean_latex = expr["latex"].replace(" ", "")
            
            # If the row contains a subscript but the user DID NOT search for one,
            # skip it to ensure 'a' doesn't flag true for a row containing 'a_{1}'
            if "_{" not in clean_name and f"{clean_name}_{{" in clean_latex:
                continue
                
            for pattern in patterns:
                if pattern in clean_latex:
                    return True
    return False


def str1(a):
    l=[]
    for i in a:
        if values(i.lower()) != "False":
            l.append(values(i.lower()))
    return l       


def values(a):
    if a.isalpha():
        return ord(a)-96
    elif a.isdigit() and int(a) !=0:
        return ord(a)-22
    elif a.isdigit() and int(a) == 0:
        return 36
    elif a == " " or a == " ":
        return 0
    else:
        return "False"
Screens = []
class screen():
    def __init__(self,sc_id,icon=(),orientation="l",colours=("crimson_red","gold","black")):

        self.name = sc_id
        Screens.append(self.name)
        self.list_but=[]
        self.list_img=[]
        if orientation == "l":
            self.width = 80
            self.length = 51
        else:
            if isinstance(orientation, str):
                orientation = orientation.lower().split("x")
            try:
                length, breadth = (int(v) for v in orientation)
            except (TypeError, ValueError):
                raise ValueError('orientation must be "l", a string like "51x80" (lengthxbreadth), or a (length, breadth) tuple')
            self.length = length
            self.width = breadth
        self.orientation = (self.length, self.width)
        self.icon=icon
        self.padding_h=2
        self.padding_w=2
        self.def_colours=colours
        self.back_to=""
        self.explist=[]
        self.key=[]
        self.label=[]

    def add_button(self,length=16,width=16,icon=False,action="",colours=(),label="",font=0.2277,exp=""):
            if colours==():
                self.list_but.append([length,width,icon,action,self.def_colours,0.5,label,font,exp])
            else:
                self.list_but.append([length,width,icon,action,colours,0.5,label,font,exp])


    def switch(self,a):

            return "{}_{{{}}} \\to 0 , {}_{{{}}} \\to 1".format(self.name[0],self.name[1::],a[0],a[1::])

    def add_label(self,label="",font=0.2277,action="",label_maxlen=0,coords=(),colour=""):
        if colour=="":
            colour=self.def_colours[1]
        self.label.append([label,font,action,label_maxlen,coords,colour])

    def back(self,a):
        self.back_to=a


    def keyboard(self,type="d",display=True,max_len=7,target="",on_enter=""):
        o=target
        if "{" not in target:
            target="{}_{{{}}}".format(target[0],target[1::])
        if target=="":
            raise Exception("Must Provide A Valid Target Variable")
        elif search_broad(target)==True:
            raise Exception("Name already exists")
        elif "{}_{{{}}}".format(self.name[0],self.name[1::])==target:
            raise Exception("Name Cannot be same as screen name")
        if max_len>15:
            print("Max Len For Keyboard of Screen {} exceeded 15. It has been changed to 15 now".format(self.name))
            max_len=15
        self.key.append([type,display,max_len,target,o,on_enter])


    def add_exp(self,exp="",colour="gold",action= False,trans_line=1,trans_bg=0.5):
        self.explist.append([exp,colour,action,trans_line,trans_bg])


    def add_image(self,length=16,width=16,icon=False,action="",colours=(),coords=(0,0),exp="",fill=0,scale="default"):
            if colours==():
                self.list_img.append([length,width,icon,action,self.def_colours,scale,exp,coords,fill])
            else:
                self.list_img.append([length,width,icon,action,colours,scale,exp,coords,fill])

    add_img = add_image  # old name, kept so existing scripts still work

    def compile(self):
        _init_graph()


        append(self.name,is_note=True)
    

        if self.name== "Main":
            append("{}_{{{}}} =1".format(self.name[0],self.name[1::]))
        else:
            append("{}_{{{}}} =0".format(self.name[0],self.name[1::]))


        append("{}_{{{}}}b_{{lkscl}}(x,y,1,1,{},{},1) \\geq 0".format(self.name[0],self.name[1::],self.width,self.length),trans_bg=1,colour="black")


        if self.icon != ():
            append("{}_{{{}}}i_{{gs}}(x-{},y-{},1,1,{},{},{},0,{}) \\geq 0".format(self.name[0],self.name[1::],self.width/2-self.icon[1]/2*(1.5*16/self.icon[0]),self.length/2-self.icon[0]/2*(1.5*16/self.icon[0]),self.icon[0],self.icon[1],self.icon[2],1.5*16/self.icon[0]),colour=self.def_colours[0],trans_lines=0,trans_bg=0.5)


        if self.back_to !="":
                append("{}_{{{}}}i_{{gs}}\\left(x-3,y-{},1,1,16,16,B_{{ack}},0,0.35\\right)\\geq 0".format(self.name[0],self.name[1::],self.length-5),action = self.switch(self.back_to),colour=self.def_colours[1],trans_bg=1,trans_lines=0)       


        length_con= self.width-2*self.padding_w
        netlen=0


        for i in self.list_but:
            netlen+=i[1]


        gap_len=(length_con-netlen)/(len(self.list_but)+1)
        
        
        for j in range(len(self.list_but)):
            L=self.list_but[j][2]
            if self.list_but[j][2]==False:
                L=[]
                for k in range(self.list_but[j][0]*self.list_but[j][1]):
                    L.append(1)
            if j == 0:
                extlen=0
            else:
                extlen= self.list_but[j-1][0]
            li=self.list_but[j]

            append(li[8]+"{}_{{{}}}i_{{gs}}(x-{},y-{},1,1,{},{},{},1,{}) \\geq 0".format(self.name[0],self.name[1::],self.padding_w+extlen+gap_len*(j+1),self.length-self.padding_h-self.list_but[j][0],self.list_but[j][0],self.list_but[j][1],L,(0.5*16/li[1])),colour=self.list_but[j][4][0],trans_lines=1,trans_bg=0.4,action=self.list_but[j][3])
            append(li[8]+"{}_{{{}}}i_{{gs}}(x-{},y-{},1,1,{},{},{},0,{}) \\geq 0".format(self.name[0],self.name[1::],self.padding_w+extlen+gap_len*(j+1),self.length-self.padding_h-self.list_but[j][0],self.list_but[j][0],self.list_but[j][1],L,(0.5*16/li[1])),colour=self.list_but[j][4][1],trans_lines=0,trans_bg=0.6,action=self.list_but[j][3])
            if li[6] != "":

                #                self.list_but.append([length,width,icon,action,self.def_colours,1,label,font,exp])

                k=str1(li[6])
                phi=li[7]
                kfin=[]
                if len(k)*7*phi>18*li[5]:
                    if 0 not in k:
                        for i in range(int(len(k)*7*phi/(18*li[5]))):
                            k1=[]
                            i1=0
                            while len(k1)*7*phi<18*li[5]:
                                k1.append(k.pop(0))
                                i1+=1
                            if k1 !=[]:
                                kfin.append(k1)
                    else:
                        for i in range(k.count(0)):
                            k1=[]
                            i1=0
                            while k[0] !=0:
                                k1.append(k.pop(0))
                                i1+=1
                            k.pop(0)
                            if k1 !=[]:
                                kfin.append(k1)

                if k !=[]:
                    kfin.append(k)
                for i2 in range(len(kfin)):
                    append("{}_{{{}}}o_{{utput}}\\left(x-{},y-{},1,1,5,7,{},{},{},{}\\right) \\geq 0".format(self.name[0],self.name[1::],self.padding_w+extlen+gap_len*(j+1)-8*phi,self.length-self.padding_h-self.list_but[j][0]-5*phi-6*phi*(i2),0,phi,8*phi,kfin[i2]),colour=self.list_but[j][4][1],trans_lines=0,trans_bg=1)
        print("self.label",self.label,self.name,self.label != [])
        if self.label != []:
            for i in self.label:
                #        self.label.append([label,font,action,label_maxlen,coords])
                k_l=str1(i[0])

                k_fin_l=[[]]
                ind=0
                while ind <len(k_l):
                    word=[]
                    while k_l[ind] !=0:
                        word.append(k_l[ind])
                        ind+=1
                    ind+=1
                    word.append(0)

                    if (len(k_fin_l[-1])+len(word))<=i[3]:
                            for t in word:
                                k_fin_l[-1].append(t)
                    else:
                            k_fin_l.append(word)

                for p in range(len(k_fin_l)):
                    append("{}_{{{}}}o_{{utput}}\\left(x-{},y-{},1,1,5,7,{},{},{},{}\\right) \\geq 0".format(self.name[0],self.name[1::],i[4][0],i[4][1]-p*8*i[1],0,i[1],8*i[1],k_fin_l[p]),colour=i[5],trans_lines=0,trans_bg=1,action=i[2])




        
        for j in range(len(self.list_img)):
            L=self.list_img[j][2]
            if self.list_img[j][2]==False:
                L=[]
                for k in range(self.list_img[j][0]*self.list_img[j][1]):
                    L.append(1)
            li=self.list_img[j]
            #elf.list_img.append([length,width,icon,action,self.def_colours,1,exp,coords,fill])
            if li[5]=="default":
                li[5]=(0.5*16/li[1])
            if li[8]==2:
                append(li[6]+"{}_{{{}}}i_{{gs}}(x-{},y-{},1,1,{},{},{},1,{}) \\geq 0".format(self.name[0],self.name[1::],li[7][0],li[7][1],li[0],li[1],L,li[5]),colour=li[4][0],trans_lines=1,trans_bg=0.4,action=li[3])
                append(li[6]+"{}_{{{}}}i_{{gs}}(x-{},y-{},1,1,{},{},{},0,{}) \\geq 0".format(self.name[0],self.name[1::],li[7][0],li[7][1],li[0],li[1],L,li[5]),colour=li[4][1],trans_lines=0,trans_bg=0.6,action=li[3])
            elif li[8]==1:
                append(li[6]+"{}_{{{}}}i_{{gs}}(x-{},y-{},1,1,{},{},{},1,{}) \\geq 0".format(self.name[0],self.name[1::],li[7][0],li[7][1],li[0],li[1],L,li[5]),colour=li[4][1],trans_lines=0,trans_bg=0.6,action=li[3])
            else:
                append(li[6]+"{}_{{{}}}i_{{gs}}(x-{},y-{},1,1,{},{},{},0,{}) \\geq 0".format(self.name[0],self.name[1::],li[7][0],li[7][1],li[0],li[1],L,li[5]),colour=li[4][1],trans_lines=0,trans_bg=0.6,action=li[3])
        
        
        if self.key !=[]:
            tem=self.key[0]
            if tem[1]:
                append("{}_{{{}}}=[]".format("D","isp"+tem[4]))
            if tem[0]=="d":
                append("{}=0".format(tem[3]),foldername=self.name + " Keyboard")
                tar=tem[3]
                for i in range(1,11):
                    append("{}_{{{}}}i_{{gs}}(x-3-{},y-4,1,1,5,7,a(d_{{{}}}),0,0.6) \\geq 0".format(self.name[0],self.name[1::],5*(i-1),i),foldername=self.name + " Keyboard",colour="blue",trans_bg=1,trans_lines=0,action="{}\\to10\\cdot {} +{}\\left\\{{\\operatorname{{ceil}}\\left(\\log_{{10}}\\left(10\\left({}+1\\right)\\right)\\right)\\le{}\\right\\}},{}_{{{}}} \\to \\operatorname{{join}}({}_{{{}}},[d_{{{}}}])\\left\\{{\\operatorname{{ceil}}\\left(\\log_{{10}}\\left(10\\left({}+1\\right)\\right)\\right)\\le{}\\right\\}}".format(tar,tar,i*int(i!=10),tar,tem[2],"D","isp"+tem[4],"D","isp"+tem[4],i,tar,tem[2]))
            List="{}_{{{}}}".format("D","isp"+tem[4])
            append("{}_{{{}}}i_{{gs}}(x-56,y-4,1,1,5,7,a(24),0,0.6)\\geq 0".format(self.name[0],self.name[1::]),colour="red",foldername=self.name + " Keyboard",trans_bg=1,trans_lines=0,action="{} \\to \\operatorname{{floor}}(\\frac{{{}}}{{10}}),{}\\to\\left\\{{{}.\\operatorname{{count}}\\ >1:{}\\left[1...{}.\\operatorname{{count}}-1\\right],\\left[\\right]\\right\\}}".format(tar,tar,List,List,List,List))
            if tem[1]:
                append("{}_{{{}}}o_{{utput}}\\left(x+2,y-9,1,1,5,7,0,0.6,5,{}\\right) \\geq 0".format(self.name[0],self.name[1::],"{}_{{{}}}".format("D","isp"+tem[4])),foldername=self.name + " Keyboard",colour="blue",trans_bg=1,trans_lines=0)
            if tem[5] !="":
                append("{}_{{{}}}i_{{gs}}(x-64,y-3.3,1,1,16,16,E_{{nter}},0,\\frac{{5}}{{16}}) \\geq 0".format(self.name[0],self.name[1::]),colour="green",foldername=self.name + " Keyboard",action=tem[5],trans_bg=1,trans_lines=0)
        
        
        if self.explist != 0:
            for i in self.explist:
                append("{}_{{{}}}".format(self.name[0],self.name[1::])+i[0],colour=i[1],action=i[2],trans_bg=i[4],trans_lines=i[3])

def run():
    """Launches an isolated user window containing the updated layout canvas with NO timeout limits."""
    _init_graph()
    print("[*] Booting localized calculator container...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto(f"https://desmos.com/calculator/{GRAPH_ID}")
        
        state_json_str = json.dumps(_graph_state)
        page.evaluate(f"Calc.setState({state_json_str});")
        
        print("[SUCCESS] Grid loaded. Close the visualization window to terminate.")
        page.wait_for_event("close", timeout=0)


def export():
    """Saves the graph state directly to cloud memory and yields a clean share URL."""
    _init_graph()
    print("[*] Initializing background cloud synchronization script...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(f"https://desmos.com/calculator/{GRAPH_ID}")
        
        state_json_str = json.dumps(_graph_state)
        page.evaluate(f"Calc.setState({state_json_str});")
        
        new_url = page.evaluate("""() => {
            return new Promise((resolve, reject) => {
                Calc.controller.dispatch({type: 'click-share-button'});
                
                let checkInterval = setInterval(() => {
                    let hash = Calc.controller.getShareHash();
                    if (hash) {
                        clearInterval(checkInterval);
                        resolve('https://desmos.com/calculator/' + hash);
                    }
                }, 200);
                
                setTimeout(() => {
                    clearInterval(checkInterval);
                    reject('Timeout generating save link');
                }, 8000);
            });
        }""")
        
        browser.close()
        print(f"\n[SUCCESS] Cloud sync complete!")
        print(f"Export Link: {new_url}")
        return new_url
