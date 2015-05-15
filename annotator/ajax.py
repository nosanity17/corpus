from dajax.core import Dajax
import json
from dajaxice.decorators import dajaxice_register
from models import Sentence


@dajaxice_register
def load_corrections(request, num):
    print 'hello'
    dajax = Dajax()
    print 'hello2'
    sent = Sentence.objects.get(pk=num).correct
    print '#'+str(num)+'+', 'innerHTML', sent
    dajax.assign('#'+str(num)+'+','innerHTML', sent)

    return dajax.json()


@dajaxice_register
def multiply(request, a, b):
    dajax = Dajax()
    result = int(a) * int(b)
    dajax.assign('#result','value',str(result))
    return dajax.json()


@dajaxice_register
def sayhello(request):
    return json.dumps({'message':'Hello World'})

