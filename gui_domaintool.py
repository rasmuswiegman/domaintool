#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, messagebox
import dns.resolver
import dns.reversename

def get_a_records(domain, resolver, text_widget):
    try:
        a_response = resolver.resolve(domain, 'A')
        text_widget.insert(tk.END, f"A Records for {domain}:\n")
        for A in a_response:
            text_widget.insert(tk.END, f"  {A}\n")
    except dns.resolver.NXDOMAIN:
        text_widget.insert(tk.END, f"No A Records found for (NXDOMAIN) {domain}\n")
    except dns.resolver.NoAnswer:
        text_widget.insert(tk.END, f"No A Records found for (NoAnswer) {domain}\n")
    except dns.exception.DNSException as e:
        text_widget.insert(tk.END, f"Error while fetching A records for {domain}\n{e}\n")

def get_dns_servers(domain, resolver, text_widget):
    try:
        ns_response = resolver.resolve(domain, 'NS')
        text_widget.insert(tk.END, f"DNS Servers for {domain}:\n")
        for ns in ns_response:
            text_widget.insert(tk.END, f"  {ns}\n")
    except dns.resolver.NXDOMAIN:
        text_widget.insert(tk.END, f"No DNS Servers found for (NXDOMAIN) {domain}\n")
    except dns.resolver.NoAnswer:
        text_widget.insert(tk.END, f"No DNS Servers found for (NoAnswer) {domain}\n")
    except dns.exception.DNSException as e:
        text_widget.insert(tk.END, f"Error while fetching DNS Servers for {domain}\n{e}\n")

def check_dnssec(domain, resolver, text_widget):
    try:
        ds_response = resolver.resolve(domain, 'DS')
        text_widget.insert(tk.END, f"DNSSEC is enabled for {domain}:\n")
        for record in ds_response:
            text_widget.insert(tk.END, f"  {record}\n")
    except dns.resolver.NXDOMAIN:
        text_widget.insert(tk.END, f"DNSSEC is not enabled for (NXDOMAIN) {domain}\n")
    except dns.resolver.NoAnswer:
        text_widget.insert(tk.END, f"No DS Records found for (NoAnswer) {domain}\n")
    except dns.exception.DNSException as e:
        text_widget.insert(tk.END, f"Error while checking DNSSEC for {domain}\n{e}\n")

def get_mx_records(domain, resolver, text_widget):
    try:
        mx_response = resolver.resolve(domain, 'MX')
        text_widget.insert(tk.END, f"MX Records for {domain}:\n")
        for MX in mx_response:
            text_widget.insert(tk.END, f"  {MX}\n")
    except dns.resolver.NXDOMAIN:
        text_widget.insert(tk.END, f"MX Records not found for (NXDOMAIN) {domain}\n")
    except dns.resolver.NoAnswer:
        text_widget.insert(tk.END, f"No MX Records found for (NoAnswer) {domain}\n")
    except dns.exception.DNSException as e:
        text_widget.insert(tk.END, f"Error while fetching Mail Servers for {domain}\n{e}\n")

def get_txt_records(domain, resolver, text_widget):
    try:
        txt_response = resolver.resolve(domain, 'TXT')
        text_widget.insert(tk.END, f"TXT records for {domain}:\n")
        for TXT in txt_response:
            text_widget.insert(tk.END, f"  {TXT}\n")
    except dns.resolver.NXDOMAIN:
        text_widget.insert(tk.END, f"TXT Records not found for (NXDOMAIN) {domain}\n")
    except dns.resolver.NoAnswer:
        text_widget.insert(tk.END, f"No TXT Records found for (NoAnswer) {domain}\n")
    except dns.exception.DNSException as e:
        text_widget.insert(tk.END, f"Error while fetching TXT Records for {domain}\n{e}\n")

def get_dmarc_policy(domain, resolver, text_widget):
    try:
        dmarc_response = resolver.resolve(f'_dmarc.{domain}', 'TXT')
        text_widget.insert(tk.END, f"DMARC Policy for {domain}:\n")
        for record in dmarc_response:
            text_widget.insert(tk.END, f"  {record}\n")
    except dns.resolver.NXDOMAIN:
        text_widget.insert(tk.END, f"DMARC Policy not found for (NXDOMAIN) {domain}\n")
    except dns.resolver.NoAnswer:
        text_widget.insert(tk.END, f"No DMARC Policy found for (NoAnswer) {domain}\n")
    except dns.exception.DNSException as e:
        text_widget.insert(tk.END, f"Error while fetching DMARC Policy for {domain}\n{e}\n")

def reverse_lookup(ip, resolver, text_widget):
    try:
        reversed_ip = dns.reversename.from_address(ip)
        ptr_response = resolver.query(reversed_ip, 'PTR')
        text_widget.insert(tk.END, f"Reverse Lookup for {ip}:\n")
        for ptr_record in ptr_response:
            text_widget.insert(tk.END, f"  {ptr_record}\n")
    except dns.resolver.NXDOMAIN:
        text_widget.insert(tk.END, f"No PTR record found for {ip}\n")
    except dns.resolver.NoAnswer:
        text_widget.insert(tk.END, f"No PTR record found for {ip}\n")
    except dns.exception.DNSException as e:
        text_widget.insert(tk.END, f"Error while performing reverse lookup for {ip}\n{e}\n")
    except Exception as e:
        text_widget.insert(tk.END, f"Unexpected error during reverse lookup for {ip}\n{e}\n")

def lookup():
    domain = entry_domain.get()
    ip = entry_ip.get()
    options = []
    text_widget.delete(1.0, tk.END)

    if var_all.get():
        options.append('-all')
    if var_dns.get():
        options.append('-dns')
    if var_ns.get():
        options.append('-ns')
    if var_mx.get():
        options.append('-mx')
    if var_dnssec.get():
        options.append('-dnssec')
    if var_txt.get():
        options.append('-txt')
    if var_a.get():
        options.append('-a')
    if var_dmarc.get():
        options.append('-dmarc')
    if var_reverse.get():
        options.append('-r')

    resolver = dns.resolver.Resolver()

    if domain:
        text_widget.insert(tk.END, f"LOOKING UP {domain}:\n")
        if '-all' in options or '-dns' in options or '-ns' in options:
            get_dns_servers(domain, resolver, text_widget)
        if '-all' in options or '-a' in options:
            get_a_records(domain, resolver, text_widget)
        if '-all' in options or '-mx' in options:
            get_mx_records(domain, resolver, text_widget)
        if '-all' in options or '-dnssec' in options:
            check_dnssec(domain, resolver, text_widget)
        if '-all' in options or '-txt' in options:
            get_txt_records(domain, resolver, text_widget)
        if '-all' in options or '-dmarc' in options:
            get_dmarc_policy(domain, resolver, text_widget)

    if ip and '-r' in options:
        text_widget.insert(tk.END, f"LOOKING UP IP - {ip}:\n")
        reverse_lookup(ip, resolver, text_widget)

root = tk.Tk()
root.title("DNS Lookup Tool")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Domain:").grid(row=0, column=0, sticky=tk.E)
entry_domain = tk.Entry(frame)
entry_domain.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="IP:").grid(row=1, column=0, sticky=tk.E)
entry_ip = tk.Entry(frame)
entry_ip.grid(row=1, column=1, padx=5, pady=5)

var_all = tk.BooleanVar()
var_dns = tk.BooleanVar()
var_ns = tk.BooleanVar()
var_mx = tk.BooleanVar()
var_dnssec = tk.BooleanVar()
var_txt = tk.BooleanVar()
var_a = tk.BooleanVar()
var_dmarc = tk.BooleanVar()
var_reverse = tk.BooleanVar()

tk.Checkbutton(frame, text="All", variable=var_all).grid(row=2, column=0, sticky=tk.W)
tk.Checkbutton(frame, text="DNS", variable=var_dns).grid(row=2, column=1, sticky=tk.W)
tk.Checkbutton(frame, text="NS", variable=var_ns).grid(row=3, column=0, sticky=tk.W)
tk.Checkbutton(frame, text="MX", variable=var_mx).grid(row=3, column=1, sticky=tk.W)
tk.Checkbutton(frame, text="DNSSEC", variable=var_dnssec).grid(row=4, column=0, sticky=tk.W)
tk.Checkbutton(frame, text="TXT", variable=var_txt).grid(row=4, column=1, sticky=tk.W)
tk.Checkbutton(frame, text="A", variable=var_a).grid(row=5, column=0, sticky=tk.W)
tk.Checkbutton(frame, text="DMARC", variable=var_dmarc).grid(row=5, column=1, sticky=tk.W)
tk.Checkbutton(frame, text="Reverse Lookup", variable=var_reverse).grid(row=6, column=0, sticky=tk.W)

btn_lookup = tk.Button(frame, text="Lookup", command=lookup)
btn_lookup.grid(row=7, column=0, columnspan=2, pady=10)

text_widget = scrolledtext.ScrolledText(root, width=80, height=20)
text_widget.pack(padx=10, pady=10)

root.mainloop()

