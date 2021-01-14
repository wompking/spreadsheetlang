import ast
import pathlib
import sys
import re
import math

if len(sys.argv) < 2:
	print("Usage: python3 SPREADSHEET.py <file>")
	sys.exit(-1)
debugging = len(sys.argv) > 2
program = open(sys.argv[1]).read()

showeval = False

def printev(*s):
	if showeval:
		print(*s)

def printde(*s):
	if debugging:
		print(*s)

ops = {
	"@": (0, "special", None),
	"$": (1, "special", None),
	"~": (1, {(float,):lambda a: 1-a,(tuple,):lambda a: (-a[0],-a[1])}, None),
	"£": (1, {(float,):lambda a: math.sign(a),(tuple,):lambda a: (math.sign(a[0]),math.sign(a[1]))}, None),
	"#": (1, {(float,):lambda a: abs(a),(tuple,):lambda a: (abs(a[0]),abs(a[1])),(str,):lambda a: len(a)}, None),
	"x": (1, {(tuple,):lambda a: a[0]}, None),
	"y": (1, {(tuple,):lambda a: a[1]}, None),
	"+": (2, {(float,float):lambda a,b:a+b,(str,str):lambda a,b:a+b,(tuple,tuple):lambda a,b:(a[0]+b[0],a[1]+b[1])}, None),
	"-": (2, {(float,float):lambda a,b:a-b,(tuple,tuple):lambda a,b:(a[0]-b[0],a[1]-b[1])}, None),
	"/": (2, {(float,float):lambda a,b:a/b,(tuple,tuple):lambda a,b:((a[0]*b[0]+a[1]*b[1])/(b[1]**2 + b[2]**2),(a[1]*b[0]-a[0]*b[1])/(b[1]**2 + b[2]**2)),(tuple,float):lambda a,b:(a[0]/b,a[1]/b)}, None),
	"*": (2, {(float,float):lambda a,b:a*b,(tuple,tuple):lambda a,b:(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]),(tuple,float):lambda a,b:(a[0]*b,a[1]*b),(str,float):lambda a,b:a*math.floor(b)}, None),
	"^": (2, {(float,float):lambda a,b:a**b}, None),#Note: complex exponentiation can be implemented but I don't want to do that right now :P
	"%": (2, {(float,float):lambda a,b:a%b,(tuple,tuple):lambda a,b:(a[0]%b[0],a[1]%b[1])}, None),
	"=": (2, {}, lambda a,b:1 if a==b else 0),
	">": (2, {(float,float):lambda a,b:1 if a>b else 0}, None),
	"<": (2, {(float,float):lambda a,b:1 if a<b else 0}, None),
	"≥": (2, {(float,float):lambda a,b:1 if a>=b else 0}, None),
	"≤": (2, {(float,float):lambda a,b:1 if a<=b else 0}, None),
	"T": (2, {(float,float):lambda a,b:(a,b)}, None),
	"C": (2, {\
		(float,float):lambda a,b:a,(float,tuple):lambda a,b:(a,a),(float,str):lambda a,b:str(a),\
		(str,float):lambda a,b:float(a),(str,tuple):lambda a,b:parseTuple(a),(str,str):lambda a,b:a,\
		(tuple,float):lambda a,b:(a[0]**2+a[1]**2)**0.5,(tuple,tuple):lambda a,b:a,(tuple,str):lambda a,b:str(a),\
		(None,float):lambda a,b:0,(None,tuple):lambda a,b:(0,0),(None,str):lambda a,b:"None",\
	}, None),
	"?": (3, "special", None),
	"X": (3, {(float,float,str):lambda a,b,c:c[int(a):int(b)]}, None)
}
tupleregex = r"^\((-?\d+(\.\d+)?),(-?\d+(\.\d+)?)\)$"
floatregex = r"^(-?\d+(\.\d+)?)$"
stringregex = "^(?P<V>(\"|'))(((\\\\(?P=V))|((?!(?P=V)).))+)(?P=V)$"
noneregex = r"^None$"
def parseTuple(s):
	f = re.findall(tupleregex, s)
	if f == []:
		return None
	f = f[0]
	if f[0] == "" or f[2] == "":
		return None
	return (float(f[0]),float(f[2]))

def parse(s):
	global ops
	s = s.strip()
	s = re.sub(r" +", " ", s)
	if s == "":
		return None
	s += " "
	slist = []
	strmodesingle = False
	strmodedouble = False
	esc = False
	token = ""
	for c in s:
		#print("parse char:",c)
		token += c
		if strmodesingle or strmodedouble:
			if c == "\\" and ( not esc ):
				esc = True
			if c == "\\" and esc:
				esc = False
		if not ( strmodesingle or strmodedouble ):
			if c == "'":
				strmodesingle = True
			if c == '"':
				strmodedouble = True
			if c == " ":
				slist.append(token.strip())
				#print("new token:", token)
				token = ""
		elif strmodesingle:
			if c == "'" and ( not esc ):
				strmodesingle = False
			if c == "'" and esc:
				esc = False
			if c not in "'\\" and esc:
				esc = False
		elif strmodedouble:
			if c == '"' and ( not esc ):
				strmodedouble = False
			if c == '"' and esc:
				esc = False
			if c not in "'\\" and esc:
				esc = False
	#print(slist)
	stack = []
	#printev(slist)
	for i in slist:
		#printev(i)
		#printev(re.findall(floatregex,i))
		if i in ops.keys():
			op = ops[i]
			if op[0] == 0:
				stack.append({i: []})
			else:
				stackcut = stack[-op[0]:]
				stack = stack[:-op[0]]
				stack.append({i: stackcut})
		elif re.findall(tupleregex,i):
			stack.append(parseTuple(i))
		elif re.findall(floatregex,i):
			stack.append(float(i))
		elif re.findall(stringregex,i):
			stack.append(eval(i))
		elif re.findall(noneregex,i):
			stack.append(None)
		else:
			sys.exit("Parse error: unknown data type for token [ '"+i+"' ] in line :\n"+s)

	return stack[0]

def evaluate(p,g,gval,depth=1):
	prefix = "\t"*depth
	try:
		return (gval[p],gval)
	except KeyError:
		pass
	try:
		get = g[p]
	except KeyError:
		return (None,gval)
	printev(prefix+"get:",get)
	if get[0] == "I":
		inp = input()
		gval[p] = inp
		printev(prefix+"returning from 0")
		return (inp,gval)
	code = get[1]
	def internal(o,gval,depth=1):
		prefix = "\t"*depth
		printev(prefix+"object:",o)
		if isinstance(o,dict):
			opstr = list(o.keys())[0]
			printev(prefix+"operator name:",opstr)
			params = o[opstr]
			printev(prefix+"params:",params)
			op = ops[opstr]
			printev(prefix+"operator data:",op)
			if opstr == "?":
				printev(prefix+"evaluating lazily since operator is ?")
				cond = internal(params[2],gval,depth=depth+1)
				printev(prefix+"conditional value:",cond)
				if cond:
					printev(prefix+"condition value is truthy")
					out = internal(params[0],gval,depth=depth+1)
					printev(prefix+"returning from 1")
					return (p,gval)
				else:
					printev(prefix+"condition value is falsey")
					out = internal(params[1],gval,depth=depth+1)
					printev(prefix+"returning from 2")
					return (p,gval)
			paramseval =  []
			for i in params:
				new = internal(i,gval,depth=depth+1)
				paramseval.append(new[0])
				gval = new[1]
			printev(prefix+"params, evaluated:",paramseval)
			paramtypes = tuple([type(i) for i in paramseval])
			printev(prefix+"param types:",paramtypes)
			if opstr == "@":
				printev(prefix+"return value:",p)
				printev(prefix+"returning from 3")
				return (p,gval)
			elif opstr == "$":
				printev(prefix+"iiit's get time!".upper())
				if paramtypes == (tuple,):
					get = evaluate(paramseval[0],g,gval,depth=depth+1)
				else:
					get = None
				printev(prefix+"got:",get)
				if get == None:
					printev(prefix+"returning from 108")
					return (None,gval)
				gval = get[1]
				printev(prefix+"returning from 4")
				return (get[0],gval)
			else:
				try:
					func = op[1][paramtypes]
				except KeyError:
					func = op[2]
				printev(prefix+"function:",func)
				if type(func) != type(lambda _: None):
					rv = func
				else:
					rv = func(*paramseval)
				printev(prefix+"return value:",rv)
				printev()
				printev(prefix+"returning from 5")
				return (rv,gval)
		else:
			printev(prefix+"returning from 5")
			return (o,gval)
	if get[0] in "SF":
		printev(prefix+"getting position")
		setpos, gval = internal(code[0],gval,depth=depth+1)
		printev(prefix+"getting value")
		setval, gval = internal(code[1],gval,depth=depth+1)
		printev(prefix+"position + value:",(setpos,setval))
		outval = None
		printev(prefix+"set out val:",outval)
		gval[p] = outval
		printev(prefix+"new grid values:",gval)
		return ((setpos,setval),gval)
	else:
		outval, gval = internal(code,gval,depth=depth+1)
		printev(prefix+"set out val:",outval)
		gval[p] = outval
		printev(prefix+"new grid values:",gval)
		return (outval,gval)

def step(g,ng,gval):
	gs = list(g.keys())
	gsf = []
	for i in gs:
		if g[i][0] in "SF":
			gsf.append(i)
	buckets = {}
	for i in gsf:
		v = (i[0]**2+i[1]**2)**0.5
		try:
			buckets[v].append(i)
		except KeyError:
			buckets[v] = [i]
	for i in buckets.keys():
		buckets[i] = sorted(buckets[i], key=lambda a: math.atan2(a[1],a[0]))
	gsfs = []
	for i in sorted(buckets.keys()):
		gsfs += buckets[i]
	for i in gsfs:
		settype = g[i][0]
		v = evaluate(i,g,gval)
		posdat = v[0]
		gval = v[1]
		if posdat == (0,0):
			settype = "S"
		if settype == "S":
			ng[posdat[0]] = ('V', posdat[1])
		else:
			f = re.findall(r"^([VSI])(\(-?\d+(\.\d+)?,-?\d+(\.\d+)?\)):?(.+?)(\/\/.+)?$", posdat[1])
			ft = (f[0][1].strip(),f[0][0].strip(),f[0][4].strip())
			if ft[1] in "SF":
				ng[parseTuple(ft[0])] = (ft[1],tuple([parse(b) for b in ft[2].split("<=")]))
			else:
				ng[parseTuple(ft[0])] = (ft[1],parse(ft[2]))
		printev("value returned:",v)
		printev("position data:",posdat)
		printev("new grid:",ng)
	return ng

programsplit = [re.findall(r"^([VSI])(\(-?\d+(\.\d+)?,-?\d+(\.\d+)?\)):?(.+?)(\/\/.+)?$", a) for a in program.split("\n")]
programsplit = [(a[0][1].strip(),a[0][0].strip(),a[0][4].strip()) for a in programsplit if a != []]
grid = {}
for a in programsplit:
	if a[1] in "SF":
		grid[parseTuple(a[0])] = (a[1],tuple([parse(b) for b in a[2].split("<=")]))
	else:
		grid[parseTuple(a[0])] = (a[1],parse(a[2]))
oldgrid = None
i = 0
while oldgrid != grid:
	if debugging:
		printde("Step number:",i)
		printde("Current grid:",grid)
	i += 1
	oldgrid = grid.copy()
	newgrid = grid.copy()
	gridvalues = {}
	grid = step(grid,newgrid,gridvalues)
	printde("Grid values:",gridvalues)
	grid = newgrid
	try:
		print(grid[(0,0)][1],end="")
		del grid[(0,0)]
	except KeyError:
		pass