'''
Demonstration of a functionally implemented FIFO queue.
Written in Python because I don't know any functional languages yet.
Supports O(1) append at front and delete from back.
'''

def pair(x, y=None):
	if y == None:
		return (x, y, 1)
	else:
		_, _, ylen = y
	return (x, y, ylen + 1) 

def _chain(iter):
	if not iter:
		return None
	return pair(iter[-1], _chain(iter[:-1]))

def pLen(p):
	if p is None:
		return 0
	_, _, ret = p
	return ret

def _pRepr(p):
	if not p:
		return []
	x, y, _ = p
	return _pRepr(y) + [x]

def head(p):
	x, _, _ = p
	return x

def tail(p):
	_, y, _ = p
	return y

def pMove(s, t):
	if pLen(s) == 0:
		return (s, t)
	else:
		return (tail(s), pair(head(s), t))

def pMoveK(s, t, k):
	if k == 0:
		return (s, t)
	else:
		return pMoveK(*pMove(s, t), k-1)

##################################################################################################
SPEED = 2

qInit = lambda: (None, None, None, 0)
''' q contains:
 - left stack
 - right stack
 - memoized arrays used under-the-hood to perform shifts from right to left stack
	- tempL, revL: keeps track of the reversal of left stack (interm. result stored in revL)
	- rempR, revR: same for right stack
 - number of deletes that have happened since the most recent qShift was initiated
'''
def qLen(q):
	left, right, _, _ = q
	return pLen(left) + pLen(right)

def qAppend(q, x):
	left, right, saved, dels = q
	if pLen(left) <= pLen(right) or saved is not None:
		return qShift(left, pair(x, right), saved, dels)
	return (left, pair(x, right), None, 0)
	
def qDelete(q):
	left, right, saved, dels = q
	if pLen(left) == 0:
		return q, None
	if pLen(left) <= pLen(right):
		left1, right1, saved1, dels1 = qShift(left, right, saved, dels)
		return (tail(left1), right1, saved1, dels1), head(left)
	return (tail(left), right, None, dels), head(left)

def qShift(left, right, saved, dels):
	# If reversal hasn't started, start it
	if saved is None:
		tempL1, revL1 = pMoveK(left, None, SPEED)
		tempR1, revR1 = pMoveK(right, None, SPEED)
		right1 = None
	# If reversal has started, continue it; this will do nothing if reversal has completed
	else:
		tempL, revL, tempR, revR = saved
		tempL1, revL1 = pMoveK(tempL, revL, SPEED)
		tempR1, revR1 = pMoveK(tempR, revR, SPEED)
		right1 = right
	# If both reversals are done, begin/continue revL->revR transfer
	if tempL1 is None and tempR1 is None:
		revL2, revR2 = pMoveK(revL1, revR1, max( pLen(revL1)-dels, SPEED ))
		# If transfer is complete, finish by replacing left with revR
		if pLen(revL2) - dels == 0:	
			return (revR2, right1, None, 0)
		else:
			return (left, right1, (tempL1, revL2, tempR1, revR2), dels)
	else:
		return (left, right1, (tempL1, revL1, tempR1, revR1), dels)
	# always return q
	
def _qRepr(q):
	left, right, saved, dels = q
	return _pRepr(left), _pRepr(right)

def _qExample(s, show=True):
	# Prints the history of a queue according to string s.
	# format: a for append, d for delete. ex: 'adaaaadddadddddadaaadddad'
	if type(s) != str:
		raise TypeError()
	if not s:
		return
	i = 0
	q = qInit()
	for c in s:
		if c == 'a':
			q = qAppend(q, i)
			if show:
				print(f"Appending {i}...")
				print(_qRepr(q))
			i += 1
		elif c == 'd':
			q, x = qDelete(q)			
			if show:
				print(f'Deleting {x}...')
				print(_qRepr(q))
		else:
			raise ValueError('_qExample only accepts strings containing "a" and "d"')

if __name__ == '__main__':
	import time, sys

	print('------VERBOSE DEMONSTRATION------')
	_qExample('addaaaaaaaaaadddddddd', show = True)

	print('------TIME COMPARISON------')
	size = int(5e3)
	# NOTE: Couldn't go higher due to recursion limit
	iters = 100
	lowDepth = 'ad' * size
	highDepth = 'a'*size + 'd'*size
	lowTime = highTime = 0
	for i in range(iters):
		start = time.time()
		_qExample(lowDepth, show=False)
		end = time.time()
		lowTime += (end-start)
	print(f'avg time spent for {size} alternating appends and deletes: {round(lowTime/iters, 5)}')
	sys.setrecursionlimit(int(1e5))
	for i in range(iters):
		start = time.time()
		_qExample(highDepth, show=False)
		end = time.time()
		highTime += (end-start)
	print(f'avg time spent for {size} appends, then {size} deletes: {round(highTime/iters, 5)}')
	

	