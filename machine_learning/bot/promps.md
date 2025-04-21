Estoy intentando crear un bot que utiliza vision para scrapear 
texto de conversaciones en la aplicacion Messenger de Facebook.

## Este bot debe ser capaz de:
 - Detectar si hay un nuevo mensaje en algunos de mis chats.
 - Utilizar el cursor del mouse para interactuar con la interfaz 
de messenger para viajar por la misma y poder entrar a cada chat
 - El bot debe de encontrar los mensajes que escribe la otra persona 
y utilizando procesamiento de imagenes y el cursor debe de seleccionar
el texto, copiarlo al portapapeles y extraerlo del mismo portapapeles
 - El bot ademas debe de saber en todo momento cual fue el ultimo mensaje
que ha visto de cada chat que tiene para no perderse y no estar infinitamente
extrayendo texto.
 - El bot debe de tener la habilidad de hacer scroll sobre el chat para ver
mensajes y por supuesto no deberia de perderse en ese proceso de hacer scroll,
deberia de saber en todo momento donde esta ubicado, tanto en el chat como en
messenger en general.
 - El bot debe de poder viajar por dos interfaces de messenger, la primera es la
interfaz estandar de messenger qeu sale por defecto cuando uno entra donde sale todas
las conversaciones que he tenido y la otra interfaz es de peticiones de mensajes donde 
para acceder a ella hay que hacer click sobre un boton con tres puntos en la parte superior izquierda
del area de chats y en el menu desplegable que sale entonce presionar sobre peticiones de mensajes.
 - En esta otra vista de peticiones de mensajes el bot debe de poder hacer lo mismo 
que en la vista por defecto, detectar nuevos mensajes en los chats, revisar un chat, extraer texto del chat
y hacer scroll sobre el chat.
 - Tener en cuenta de que el bot debe de viajar por las dos interfaces cada un tiempo determinado como pueden ser 5 segundos
en caso de que no hayan nuevos mensajes o no este extrayendo nada en la interfaz actual.

## Mas funcionalidades y caracteristicas que debe de tener y hacer el bot:
 - El bot debe de reconocer primero que la aplicacion o interfaz que esta en la pantalla
es messenger, esto se hace actualmente utilizando procesamiento de imagenes
 - El bot debe de establecer una conexion persistente por web socket con un servidor para enviarle 
los textos extraidos y recibir informacion del mismo ya que el bot debe de ser controlado remotamente
 - Debemos de tener en cuenta de que dentro del area del chat donde el bot navega con el scroll para extraer lo que 
escribe la otra persona puede haber texto pequeño o de tamaño normal pero tambien puede haber texto muy largo que sobresalga
mucho y se tenga que hacer mucho scroll para poder verlo todo, eso tambien es importante tenerlo en cuenta.


## De todas estas cosas que hace el bot ya yo he implementado algunas en el codigo que te voy a pasar, 
## de todas estas he implementado las siguientes:
 - Detectar si la aplicacion qeu esta en pantalla y esta capturando mediante imagenes es messenger o no
 - Detectar si hay nuevos mensajes en alguno de los chats
 - Viajar hacia esos chats que tienen nuevos mensajes haciendo click sobre ellos.
 - Navegar por el area de chat o la conversacion extrayendo texto y haciendo scroll para navegar por el
 - Tambien tiene en cuenta por donde se quedo o cual fue el ultimo texto extraido ya que se utiliza la base de 
datos sqlite para almacenar cierta informacion del bot
 - Detecta textos muy largos cuando esta navegando por el chat y sabe cuando hacer cierta cantidad de scroll 
para extraer estos textos largos o textos mas pequeños, el tratamiento es diferente para cada uno a la hora de hacer scroll
 - Tambien puede viajar entre las dos interfaces de messenger, la que esta por defecto y la de peticiones de mensajes
 - Tiene la conexion por web socket con el servidor y es capaz de mandar mensajes


## Que utiliza el bot para hacer todo esto
Para realizar todas esta funciones se estan utilizando diferentes tecnicas como procesamiento de imagenes con la libreria 
OpenCv como deteccion de contornos, manejo del cursor y del teclado con la libreria pyautogui, manejo de la base de datos con la libreria sqlalchemy,
la libreria websockets para la conexion con el servidor. Estas son todas las librerias actualmente en uso para el bot
 
- opencv-python==4.11.0.86
- PyAutoGUI==0.9.54
- SQLAlchemy==2.0.39
- pyperclip==1.9.0
- pytest==8.3.5
- websockets==15.0.1
- scikit-image==0.25.2

El codigo y la logica esta separada en diferentes clases donde cada una se encarga de diferentes objetivos, por ejemplo

1 - Imghandler: esta clase se encarga de manejar las imagenes y contiene todas las herramientas necesarias para el procesamiento de imagenes
2 - WindowHandler: esta clase se encargaria de manejar ventanas del sistema operativo pero aun no se esta utilizando
3 - Bot: esta clase se encarga de la logica del bot, tiene dentro todas las funcionalidades que puede realizar el bot
4 - WebSocket: esta clase se encarga de la conexion con el servidor y se encarga de mandar y recibir mensajes

En base a todo este contexto que te estoy dando y toda esta informacion yo necesito que me ayudes
a mejorar y arreglar la logica del bot porque estoy teneindo algunos problemas con esta funcionalidades

## Los problemas que estoy teniendo son:
 - Fallos de precision a la hora de navegar por el chat cuando se mezclan textos muy largos con textos pequeños, 
cuando pasa esto el bot se pierde.
 - Cuando se cambia de computadora y por ende de pantalla ya no detecta igual los contornos principales como el de los chats,
el del area de chat donde estan los mensajes y por ende ya no es capaz de detectar cuando hay nuevos mensajes ni de detectar textos
 - Hay que hacer que el bot sea lo mas general posible para que sirva para, si es posible todas las pantallas posibles, esto podria depender 
de una configuracion previa
 - En general el bot tiene varios problemas, otra cosa que quiero que hagas es analizar el codigo y mejorarlo para disminuir el margen de error
y reducir esos problemas posibles que pueden suceder


Te voy a pasara continuacion algunas imagens de como se ve la interfaz de messenger y los chats, etc para que 
entiendas un poco mejor y tengas mas contextos de lo que esoty haciendo.

   
Y ademas por ultimo te voy a dar todo el codigo que he creado hasta ahora, por favor necesito que lo analices bien y me ayudes.
Mi vida depende de ello, ademas te voy a recompensar muy muy bien si me ayudas y logramos que funcione bien. Seremos muy famosos si lo 
conseguimos.
