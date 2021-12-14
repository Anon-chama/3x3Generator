import PySimpleGUI as sg
import subprocess
from tkinter.filedialog import askopenfilename
import PIL.Image
import io
import base64
import os
from playsound import playsound


def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()


os.system('del audiopre\*.wav')
os.system('del images\*.png')
layout = [[],[],[], [sg.Button('Generate'),]]
filenames = ['', '', '', '', '', '', '', '', '', '']
starts = ['', '', '', '', '', '', '', '', '', '']
ends = ['', '', '', '', '', '', '', '', '', '']
minuteslist = []
totallength = 0
n=0
i = 0
while i < 10:
    j = 0
    while j < 60:
        minuteslist.append(f'{str(i).zfill(2)}:{str(j).zfill(2)}')
        j+=1
    i+=1

i = 0
while i < 3:
    j = 0
    while j < 3:
        layout[i].append(sg.Column(
            layout=[[sg.Input('', key='fileroute-'+str(i+3*j+1), size=(50, 1), disabled=True)],
                    [sg.Image(key='image-'+str(i+3*j+1), size=(150, 150), background_color='gray'),
                     sg.Column(layout=[[sg.Button('Browse', key='button-'+str(i+3*j+1))],
                                       [sg.Text('From:\t'),sg.Spin(minuteslist, key='spinstart-'+str(i+3*j+1), disabled=True)],
                                       [sg.Text('To:\t'), sg.Spin(['00:00'], key='spinend-' + str(i + 3 * j + 1), disabled=True)],
                                       [sg.Button('Preview', key='preview-'+str(i+3*j+1))]
                                       ])],]
        ))
        j+=1
    i+=1


window = sg.Window("3x3 Generator", layout)

while True:
    event, values = window.read()

    if event in('button-1','button-2', 'button-3', 'button-4', 'button-5', 'button-6', 'button-7', 'button-8', 'button-9'):
        active = event.split('-')[1]
        filename = askopenfilename()
        filenames[int(active)] = filename
        title = filename.split('/')[-1]
        subprocess.run(["ffmpeg", '-y', "-i", filename, "-an", '-vcodec', 'copy', 'images/'+active+'.png'])
        try:
            window['image-'+active].update(data = convert_to_bytes('images/'+active+'.png', (150,150)))
            window['fileroute-'+active].Update(title)
            duration = subprocess.Popen(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            duration, err = duration.communicate()
            duration = int(str(duration).partition('.')[0][2:])
            window['spinstart-'+active].Update(values= minuteslist[:duration], disabled = False)
            window['spinend-'+active].Update(values= minuteslist[:duration], disabled = False)
        except:
            print('oopsie')
    if event in('preview-1','preview-2', 'preview-3', 'preview-4', 'preview-5', 'preview-6', 'preview-7', 'preview-8', 'preview-9'):
        n+=1
        active = event.split('-')[1]
        if (values['spinstart-' + str(active)] >= values['spinend-' + str(active)]):
            sg.Popup('Error', 'End time must be greater than starting time.')
            continue
        subprocess.run(['ffmpeg', '-y', '-i', filenames[int(active)], '-ss', values['spinstart-'+active], '-to', values['spinend-'+active], '-acodec', 'copy', f'audiopre/{n}.wav'])
        playsound(f'audiopre/{n}.wav', False)

    if event == 'Generate':
        totallength = 0
        error = False
        for x in range(1, 10):
            if(filenames[x]) == '':
                sg.Popup('Error', 'You must fill all squares')
                error = True
                break
            if(values['spinstart-'+str(x)] >= values['spinend-'+str(x)]):
                title = filenames[x].split('/')[-1]
                sg.Popup('Error', f'End time on song {title} must be greater than starting time.')
                error = True
                break
            else:
                starts[x] = values['spinstart-'+str(x)]
                ends[x] = values['spinend-'+str(x)]
                totallength += minuteslist.index(ends[x]) - minuteslist.index(starts[x]) + 1
        if error:
            continue
        subprocess.run([
            "ffmpeg", "-i", filenames[1], "-i", filenames[4], "-i", filenames[7], "-i", filenames[2], "-i", filenames[5], "-i", filenames[8],
            "-i",
            filenames[3], "-i", filenames[6], "-i", filenames[9],
            "-filter_complex",
            '[0:v]scale=300:300[a];[1:v]scale=300:300[b];[2:v]scale=300:300[c];[3:v]scale=300:300[d];[4:v]scale=300:300[e];[5:v]scale=300:300[f];[6:v]scale=300:300[g];[7:v]scale=300:300[h];[8:v]scale=300:300[i];' +
            f'[0:a]atrim={minuteslist.index(starts[1])}:{minuteslist.index(ends[1])}[j];[1:a]atrim={minuteslist.index(starts[4])}:{minuteslist.index(ends[4])}[k];[2:a]atrim={minuteslist.index(starts[7])}:{minuteslist.index(ends[7])}[l];[3:a]atrim={minuteslist.index(starts[2])}:{minuteslist.index(ends[2])}[m];[4:a]atrim={minuteslist.index(starts[5])}:{minuteslist.index(ends[5])}[n];[5:a]atrim={minuteslist.index(starts[8])}:{minuteslist.index(ends[8])}[o];[6:a]atrim={minuteslist.index(starts[3])}:{minuteslist.index(ends[3])}[p];[7:a]atrim={minuteslist.index(starts[6])}:{minuteslist.index(ends[6])}[q];[8:a]atrim={minuteslist.index(starts[9])}:{minuteslist.index(ends[9])}[r];' +
            '[j][k][l][m][n][o][p][q][r]concat=n=9:v=0:a=1[s];' +
            f'[a][b][c]hstack=inputs=3[t]; [d][e][f]hstack=inputs=3[u]; [g][h][i]hstack=inputs=3[v]; [t][u][v]vstack=inputs=3[w]; [w]setpts=N/FRAME_RATE/TB[x]; [x]trim=0:{totallength}[y]; [s]asetpts=N/SR/TB[z]',
            '-map', '[y]', '-map', '[z]', '-c:a', 'libvorbis', '-c:v', 'libvpx', "-q:a", "6", "-b:v", "1000k",
            "-shortest",
            'output.webm'
        ])
        break


    if event == sg.WIN_CLOSED:
        break

window.close()
os.system('del images\*.png')