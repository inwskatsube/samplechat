# -*- coding: utf-8 -*-

import tkinter as tk
import socket
from threading import Thread
import argparse
import datetime

DEFAULT_PORT = '8001'

class MainFrm(tk.Frame):
    _textIp = None
    _textPort = None
    _msgLog = None
    _msgSend = None
    _ip = "127.0.0.1"
    _port = DEFAULT_PORT
    _sv_ip = "0.0.0.0"
    _sv_port = DEFAULT_PORT

    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()
        self.pack(fill=tk.X)

    def create_widgets(self):

        tk.Label(text="メッセージ履歴", anchor="w", width=600).pack(side=tk.TOP, fill=tk.X)
        frame1 = tk.Frame(relief=tk.FLAT)
        frame1.grid_propagate(False)
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_columnconfigure(0, weight=1)
        self._msgLog = tk.Text(frame1, borderwidth=3, relief="flat", height=16, width=600)
        self._msgLog.tag_config('recvmsg', background="white", foreground="red")
        self._msgLog.tag_config('info', background="white", foreground="green")
        self._msgLog.pack(fill=tk.Y)
        scrollb = tk.Scrollbar(frame1, command=self._msgLog.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self._msgLog['yscrollcommand'] = scrollb.set
        frame1.pack()

        tk.Label(text="メッセージ", anchor="w", width=600).pack(side=tk.TOP, anchor=tk.W)
        frame2 = tk.Frame(relief=tk.FLAT)
        frame2.grid_propagate(False)
        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)
        self._msgSend = tk.Text(frame2, borderwidth=3, relief="sunken", height=8, width=600)
        self._msgSend.pack(fill=tk.Y)
        scrollb = tk.Scrollbar(frame2, command=self._msgLog.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self._msgSend['yscrollcommand'] = scrollb.set
        frame2.pack(side=tk.TOP)
 
        frame3 = tk.Frame(relief=tk.FLAT)
        tk.Label(frame3, width=20, text="送信先 IPアドレス/ポート番号", anchor="w").pack(side=tk.LEFT)
        self._textIp = tk.Entry(frame3, width=18)
        self._textIp.pack(side=tk.LEFT)
        self._textPort = tk.Entry(frame3, width=6, text=DEFAULT_PORT)
        self._textPort.pack(side=tk.LEFT)
        tk.Button(frame3, text=' メッセージ送信 ', command=self.btnSend_click).pack(side=tk.LEFT)
        frame3.pack(side=tk.TOP, fill=tk.Y)

        self._textIp.insert(tk.END, self._ip)
        self._textPort.insert(tk.END, self._port)


    def btnSend_click(self):
        msg = self._msgSend.get("1.0", tk.END).strip()
        if msg == "": return
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(3)
        print(self._textIp.get())
        print(self._textPort.get())
        sock.connect((self._textIp.get(), int(self._textPort.get())))
        sock.sendall(msg.encode())
        self._msgLog.insert(tk.END, "【送信 to %s:%s】%s\n" % (self._textIp.get(),self._textPort.get(),datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")))
        self._msgLog.insert(tk.END, msg + "\n\n")
        self._msgLog.see(tk.END)
        self._msgSend.delete('1.0', tk.END)

    def startServer(self, port):
        self._sv_port = port
        th = Thread(target=self.process, args=())
        th.daemon = True 
        th.start()
        return self

    def process(self):
        (clinet_name, _, ipaddrlist) = socket.gethostbyname_ex(socket.gethostname())
        self._msgLog.insert(tk.END, "クライアント名: %s\n" % (clinet_name), 'info')
        idx = 1
        for ipaddr in ipaddrlist:
            self._msgLog.insert(tk.END, "クライアントIP%s: %s\n" % (idx, ipaddr), 'info')
            idx += 1
        self._msgLog.insert(tk.END, "\n")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self._sv_ip, int(self._sv_port)))
        while True:
            s.listen(1)
            conn, addr = s.accept()
            print(addr)
            while True:
                try:
                    data = conn.recv(10240)
                    if not data:
                        break
                    msg = data.decode()
                    self._msgLog.insert(tk.END, "【受信 from %s:%s】%s\n" % (addr[0], addr[1], datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")), 'recvmsg')
                    self._msgLog.insert(tk.END, msg + "\n\n", 'recvmsg')
                    self._msgLog.see(tk.END)

                except socket.error:
                    print('socket.error', flush=True)
                    conn.close()
                    break

def main():
    port = DEFAULT_PORT
    parser = argparse.ArgumentParser(prog="chat", allow_abbrev=False, description='チャットプログラム')
    parser.add_argument("-p", "--port", metavar="port", help="待ち受けるPORT番号(デフォルト: 8001)")
    args = parser.parse_args()
    if args.port: port = args.port

    root = tk.Tk()
    root.title("chat")
    root.geometry("600x400")
    frm = MainFrm(master=root)
    frm.startServer(port)
    frm.mainloop()

if __name__ == '__main__':
    main()
