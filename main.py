import os
import re
import sys
import subprocess
import vobject
import pickle
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyrogram import Client, filters, idle
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
from pyrogram.errors import FloodWait

#====================
#Initiator Install dbs
#====================

bot = Client(
    name="_",
    api_id=you_api_id,
    api_hash="you_api_has",
    bot_token="you_bot_token
    )

OWNER_ID = [you_id]

#====================
#Function Converting!
#====================

def remove_numbers(name):
    return re.sub(r'\d+', '', name).strip()

def read_vcf(file_path):
    with open(file_path, 'r') as file:
        vcard_data = file.read()
    return vobject.readComponents(vcard_data)

def write_vcf(contacts, file_path):
    with open(file_path, 'w') as file:
        for contact in contacts:
            file.write(contact.serialize())

def remove_emojis(text):
    # Regular expression pattern to match emojis
    emoji_pattern = re.compile(
        "[" 
        u"\U0001F600-\U0001F64F"  # Emoticons
        u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        u"\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def rename_contacts(contacts):
    renamed_contacts = []
    for index, contact in enumerate(contacts, start=1):
        if hasattr(contact, 'fn'):
            clean_name = remove_numbers(contact.fn.value)
            clean_name = remove_emojis(clean_name)
            contact.fn.value = f'{clean_name} {index}'
        renamed_contacts.append(contact)
    return renamed_contacts
def split_vcf(input_file, newna, contacts_per_file=100):
    contacts = list(read_vcf(input_file))
    total_contacts = len(contacts)
    file_count = (total_contacts + contacts_per_file - 1) // contacts_per_file  # Efficient way to calculate the number of files
    dump_ = []
    for i in range(file_count):
        start = i * contacts_per_file
        end = min(start + contacts_per_file, total_contacts)
        contacts_chunk = rename_contacts(contacts[start:end])
        output_file = f'{newna}-{i+1}.vcf'
        write_vcf(contacts_chunk, output_file)
        dump_.append(output_file)
    return dump_

def split_cut_vcf(input_file, namectc, dibagi_menjadi_bagian=1):
    contacts = list(read_vcf(input_file))
    contacts = rename_contacts(contacts)
    total_contacts = len(contacts)
    contacts_per_file = (total_contacts + dibagi_menjadi_bagian - 1) // dibagi_menjadi_bagian
    dump_ = []
    file_index = 1
    current_contacts = []
    for contact in contacts:
        current_contacts.append(contact)
        if len(current_contacts) == contacts_per_file and file_index < dibagi_menjadi_bagian:
            output_file = f'{namectc.replace(".vcf", "")}-{file_index}.vcf'
            write_vcf(rename_contacts(current_contacts), output_file)
            dump_.append(output_file)
            current_contacts = []
            file_index += 1
    if current_contacts:
        output_file = f'{namectc.replace(".vcf", "")}-{file_index}.vcf'
        write_vcf(rename_contacts(current_contacts), output_file)
        dump_.append(output_file)
    return dump_

def merge_vcf_files(file_paths, output_file_path):
    merged_contacts = []
    for file_path in file_paths:
        contacts = read_vcf(file_path)
        merged_contacts.extend(contacts)
    write_vcf(merged_contacts, f"{output_file_path}.vcf")

def create_vcf_entry(phone_number, contact_name):
    vcf_entry = f"""BEGIN:VCARD
VERSION:3.0
FN:{contact_name}
TEL;TYPE=CELL:{"+" if not str(phone_number).startswith("0") else ""}{phone_number}
END:VCARD
"""
    return vcf_entry

def create_vcf_file(phone_numbers, ctcname, file_name):
    with open(file_name, "w") as file:
        for i, phone_number in enumerate(phone_numbers):
            vcf_entry = create_vcf_entry(phone_number, f"{ctcname}-{i+1}")
            file.write(vcf_entry + "\n")
    return(file_name)

def create_vcf_nvy_file(phone_numbers, ctcname, file_name):
    with open(file_name, "w") as file:
        for i, phone_number in enumerate(phone_numbers):
            vcf_entry = create_vcf_entry(phone_number, f"ADMIN-{i+1}")
            file.write(vcf_entry + "\n")
        for i, phone_number in enumerate(ctcname):
            vcf_entry = create_vcf_entry(phone_number, f"NAVY-{i+1}")
            file.write(vcf_entry + "\n")
    return(file_name)

def extract_numbers_from_file(file_path):
    numbers = []
    with open(file_path, 'r') as file:
        content = file.read()
        numbers = re.findall(r'\d+', content)
    return numbers

def process_filesgbg(file_paths, output_file):
    all_numbers = []
    for file_path in file_paths:
        if os.path.isfile(file_path):
            numbers = extract_numbers_from_file(file_path)
            all_numbers.extend(numbers)
        else:
            print(f"File {file_path} tidak ditemukan.")
    with open(output_file, 'w') as file:
        for number in all_numbers:
            file.write(number + '\n')

def extract_phone_numbers(vcf_file_path, output_txt_file_path):
    with open(vcf_file_path, 'r') as vcf_file:
        vcf_content = vcf_file.read()
    vcard_list = vobject.readComponents(vcf_content)
    with open(output_txt_file_path, 'w') as txt_file:
        for vcard in vcard_list:
            if hasattr(vcard, 'tel'):
                for tel in vcard.tel_list:
                    txt_file.write(tel.value + '\n')

def hapus_spasi_antar_nomor(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    modified_lines = [''.join(line.split()) + '\n' for line in lines]
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)
    modified_lines = [line.replace('-', '') for line in modified_lines]
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)
    modified_lines = [line.replace('(', '') for line in modified_lines]
    modified_lines = [line.replace(')', '') for line in modified_lines]
    modified_lines = [line.replace('/', '') for line in modified_lines]
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)
        
def hapus_spasi_antar_nomor(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    modified_lines = [''.join(line.split()) + '\n' for line in lines]

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)
      
    modified_lines = [line.replace('-', '') for line in modified_lines]
    modified_lines = [line.replace('(', '') for line in modified_lines]
    modified_lines = [line.replace(')', '') for line in modified_lines]
    modified_lines = [line.replace('/', '') for line in modified_lines]
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)


#====================
#Database and Coin
#====================

class dbs:
    _buyer = {}

def save_data():
    with open('data.pkl', 'wb') as file:
        pickle.dump(dbs._buyer, file)

def load_data():
    with open('data.pkl', 'rb') as file:
        data = pickle.load(file)
        return data

def parse_timedelta(time_str):
    pattern = r'(\d+)([hmb])'
    time_dict = {'h': 'days', 'm': 'weeks', 'b': 'months'}
    matches = re.findall(pattern, time_str)
    if not matches:
        return None
    kwargs = {'days': 0, 'weeks': 0, 'months': 0}
    for value, unit in matches:
        kwargs[time_dict[unit]] += int(value)
    return kwargs

def add_time_delta(current_time, time_str):
    delta_dict = parse_timedelta(time_str)
    if not delta_dict:
        return None
    new_time = current_time + timedelta(days=delta_dict['days'], weeks=delta_dict['weeks'])
    new_time = new_time + relativedelta(months=delta_dict['months'])
    return new_time

#====================
#Filters User And More
#====================

home_keyboard = ReplyKeyboardMarkup([[KeyboardButton("💎 Status 💎")], [KeyboardButton("️📨 ADM & NVY 📨"), KeyboardButton("🚧 RAPIKAN TXT 🚧")], [KeyboardButton("📊 POTONG VCF 📊"), KeyboardButton("️📨 MSG to TXT 📨")], [KeyboardButton("🏷️ TXT to VCF 🏷️"), KeyboardButton("📊 BAGI VCF 📊")], [KeyboardButton("🚀 XLS to VCF 🚀"), KeyboardButton("♻️ VCF to TXT ♻️")], [KeyboardButton("🗄️ Gabung TXT 🗄️"), KeyboardButton("🗄️ Gabung VCF 🗄️")]], resize_keyboard=True)

def on_msg(pilter=None):
    def wrapper(func):
        @bot.on_message(pilter)
        async def wrapped_func(client, message):
            try:
                await func(client, message)
            except Exception as err:
                await message.reply(f"Errors:\n{err}")
        return wrapped_func
    return wrapper

def on_txt(message):
    if message.document:
        if message.document.file_name.endswith(".txt"):
            return True
    return False

def on_vcf(message):
    if message.document:
        if message.document.file_name.endswith(".vcf"):
            return True
    return False

def on_xls(message):
    if message.document:
        if message.document.file_name.endswith(".xls") or message.document.file_name.endswith(".xlsx"):
            return True
    return False

def ngecek_(user_id):
    if not dbs._buyer[user_id]:
        return False
    return True

def batals(text):
    if text == "❌ Batal ❌":
        return True
    return False

#====================
#Core Modules initiator
#====================

@on_msg(filters.command("start") & filters.private)
@on_msg(filters.command("❌ Batal ❌", "") & filters.private)
async def start_(client, message):
    user_id = message.from_user.id
    text = f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>"
    await message.reply(text, reply_markup=home_keyboard)
    if user_id not in dbs._buyer:
        dbs._buyer[user_id] = None
        save_data()

@on_msg(filters.command("🚧 Rapikan TXT 🚧", "") & filters.private)
async def ngecremotate(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .txt)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_txt(ask1) or batals(ask1.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    hapus_spasi_antar_nomor(file)
    try:
        await message.reply_document(file)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(file)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass
    os.remove(file)

@on_msg(filters.command("💎 Status 💎", "") & filters.private)
async def statues(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    namonyo = f"{message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name else ''}"
    txt = f"<b>ID:</b> <code>{message.from_user.id}</code>\n<b>Nama:</b> <code>{namonyo}</code>\n<b>Expired:</b> <code>{str(dbs._buyer[message.from_user.id])[:19]}</code>\n\n"
    await message.reply(txt)

@on_msg(filters.command("️📨 MSG to TXT 📨", "") & filters.private)
async def ngecreate(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    ask1 = await client.ask(text="<b><i>Masukkan nomor yang ingin anda ubah jadi file!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask1.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    newname = ask2.text
    with open(f"{newname}.txt", 'w') as file:
        file.write(ask1.text)
    try:
        await message.reply_document(f"{newname}.txt")
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(f"{newname}.txt")
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass
    return os.remove(f"{newname}.txt")

@on_msg(filters.command("️📨 ADM & NVY 📨", "") & filters.private)
async def ngecreatenvy(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    ask1 = await client.ask(text="<b><i>Masukkan nomor admin!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask1.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    ask2 = await client.ask(text="<b><i>Masukkan nomor navy!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    dmp_adm = []
    dmp_nvy = []
    for i in ask1.text.split():
        dmp_adm.append(i)
    for i in ask2.text.split():
        dmp_nvy.append(i)
    newname = 'ADMIN_&_NAVY.vcf'
    create_vcf_nvy_file(dmp_adm, dmp_nvy, newname)
    try:
        await message.reply_document(newname)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(newname)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass
    return os.remove(newname)

@on_msg(filters.command("🚀 XLS to VCF 🚀", "") & filters.private)
async def ngexlseate(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .xls)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_xls(ask1):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i></b>Proses dibatalkan</i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".txt", "")
    else:
        newname = ask2.text
    ask3 = await client.ask(text="<b><i>Masukkan nama contact baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask3.text or batals(ask3.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask3.text == "⭕️ Skip ⭕️":
        newnamk = ask2.text
    else:
        newnamk = ask3.text
    cont_all = []
    df = pd.read_excel(file)
    ls_cont = df.values.flatten().tolist()
    for isi in ls_cont:
        isi_ = str(isi).replace("+", "")
        if isi_.isnumeric():
            cont_all.append(isi_)
    if not cont_all:
        return await message.reply("<b><i>Contact tidak ditemukan!</b></i>")
    dump_ = create_vcf_file(cont_all, newnamk, f'{newname}.vcf')
    try:
        await message.reply_document(dump_)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(dump_)
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass
    os.remove(dump_)
    os.remove(file)

@on_msg(filters.command("🏷️ TXT to VCF 🏷️", "") & filters.private)
async def ngecreate(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .txt)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_txt(ask1) or batals(ask1.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".txt", "")
    else:
        newname = ask2.text
    ask3 = await client.ask(text="<b><i>Masukkan nama contact baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask3.text or batals(ask3.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask3.text == "⭕️ Skip ⭕️":
        newnamk = ask2.text
    else:
        newnamk = ask3.text
    cont_all = []
    with open(file, 'r') as f:
        ls_cont = f.read().split()
        for isi in ls_cont:
            isi_ = isi.replace("+", "")
            if isi_.isnumeric():
                cont_all.append(isi_)
    if not cont_all:
        return await message.reply("<b><i>Contact tidak ditemukan!</b></i>")
    dump_ = create_vcf_file(cont_all, newnamk, f'{newname}.vcf')
    try:
        await message.reply_document(dump_)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_document(dump_)
    except:
        pass
    await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    os.remove(dump_)
    os.remove(file)

@on_msg(filters.command("📊 BAGI VCF 📊", "") & filters.private)
async def ngevcfkan(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .vcf)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_vcf(ask1):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".cvf", "")
    else:
        newname = ask2.text
    ask3 = await client.ask(text="<b><i>Masukkan berapa jumlah file barunya!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask3.text or not ask3.text.isnumeric() or ask3.text == "0":
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    hsl = split_cut_vcf(file, newname, int(ask3.text))
    for isi in hsl:
        try:
            await message.reply_document(isi)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_document(isi)
        except:
            pass
        os.remove(isi)
    os.remove(file)
    try:
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass

@on_msg(filters.command("📊 POTONG VCF 📊", "") & filters.private)
async def ngevcfkan(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .vcf)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_vcf(ask1):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".vcf", "")
    else:
        newname = ask2.text
    ask3 = await client.ask(text="<b><i>Masukkan jumlah contact per filenya!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask3.text or not ask3.text.isnumeric():
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    hsl = split_vcf(file, newname, int(ask3.text))
    for isi in hsl:
        try:
            await message.reply_document(isi)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_document(isi)
        except:
            pass
        os.remove(isi)
    os.remove(file)
    try:
        await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    except:
        pass

@on_msg(filters.command("🗄️ Gabung VCF 🗄️", "") & filters.private)
async def ngecreategabung(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    allfile = []
    while True:
        asking = await client.ask(text="<b><i>Kirim file yang ingin anda gabung! (wajib .vcf)\n\nNote: Jika sudah memasukkan 2 file / lebih anda dapan menekan tombol done</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Done ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
        if asking.text:
            if batals(asking.text):
                return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
            elif asking.text == "⭕️ Done ⭕️":
                if len(allfile) < 2:
                    return await message.reply("<b><i>Proses gagal, mohon masukkan 2 file atau lebih!!</b></i>", reply_markup=home_keyboard)
                break
        elif not on_vcf(asking):
            return await message.reply("<b><i>File invalid, proses dibatalkan!!</b></i>", reply_markup=home_keyboard)
        file = await asking.download()
        allfile.append(file)
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    merge_vcf_files(allfile, ask2.text)
    await message.reply_document(f"{ask2.text}.vcf")
    await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    allfile.append(f"{ask2.text}.vcf")
    for isine in allfile:
        os.remove(isine)

@on_msg(filters.command("🗄️ Gabung TXT 🗄️", "") & filters.private)
async def ngecreatetxtgbg(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    allfile = []
    while True:
        asking = await client.ask(text="<b><i>Kirim file yang ingin anda gabung! (wajib .txt)\n\nNote: Jika sudah memasukkan 2 file / lebih anda dapan menekan tombol done</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Done ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
        if asking.text:
            if batals(asking.text):
                return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
            elif asking.text == "⭕️ Done ⭕️":
                if len(allfile) < 2:
                    return await message.reply("<b><i>Proses gagal, mohon masukkan 2 file atau lebih!!</b></i>", reply_markup=home_keyboard)
                break
        elif not on_txt(asking):
            return await message.reply("<b><i>File invalid, proses dibatalkan!!</b></i>", reply_markup=home_keyboard)
        file = await asking.download()
        allfile.append(file)
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!!</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    process_filesgbg(allfile, f"{ask2.text}.txt")
    await message.reply_document(f"{ask2.text}.txt")
    await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    allfile.append(f"{ask2.text}.txt")
    for isine in allfile:
        os.remove(isine)

@on_msg(filters.command("♻️ VCF to TXT ♻️", "") & filters.private)
async def ngetxtkanvcf(client, message):
    user_id = message.from_user.id
    ngecek = ngecek_(user_id)
    if not ngecek:
        return await message.reply("<b><i>Anda tidak memiliki akses untuk menggunakan bot ini</b></i>")
    ask1 = await client.ask(text="<b><i>Kirim file yang ingin anda convert! (wajib .vcf)</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not on_vcf(ask1):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    file = await ask1.download()
    ask2 = await client.ask(text="<b><i>Masukkan nama file baru!\nJika ingin sama seperti file sebelumnya klik skip</b></i>", user_id=user_id, chat_id=user_id, reply_markup=ReplyKeyboardMarkup([[KeyboardButton("⭕️ Skip ⭕️")], [KeyboardButton("❌ Batal ❌")]], resize_keyboard=True))
    if not ask2.text or batals(ask2.text):
        return await message.reply("<b><i>Proses dibatalkan</b></i>", reply_markup=home_keyboard)
    elif ask2.text == "⭕️ Skip ⭕️":
        newname = ask1.document.file_name.replace(".vcf", ".txt")
    else:
        newname = f"{ask2.text}.txt"
    extract_phone_numbers(file, newname)
    await message.reply_document(newname)
    await message.reply(f"<b><i>👋🏻 Hai!, {message.from_user.first_name},\n\nSelamat datang di {client.me.mention}!\nSaya dapat convert file secara instan</b></i>", reply_markup=home_keyboard)
    os.remove(file)
    os.remove(newname)

@on_msg(filters.command("add") & filters.user(OWNER_ID))
async def add_(client, message):
    if len(message.text.split()) <= 2 or not message.text.split()[1].isnumeric() or not message.text.split()[2].endswith(("h", "m", "b")):
        return await message.reply("Input wajib valid\n\nContoh: <code>/add 92732991 1b</code>\n\nNote: b = bulan, m = minggu, h = hari")
    _, user_id, timeny = message.text.split()[0:3]
    waktu_lama = dbs._buyer.get(int(user_id))
    if waktu_lama:
        waktuny = waktu_lama
    else:
        waktuny = datetime.now()
    new_time = add_time_delta(waktuny, timeny.lower())
    if not new_time:
        return await message.reply("Input wajib valid\n\nContoh: <code>/add 92732991 1b</code>\n\nNote: b = bulan, m = minggu, h = hari")
    dbs._buyer[int(user_id)] = new_time
    save_data()
    await message.reply(f"<b><i>Berhasil menambahkan {user_id} selama {timeny}</b></i>")

@on_msg(filters.command("remove") & filters.user(OWNER_ID))
async def remove_(client, message):
    if len(message.text.split()) != 2 or not message.text.split()[1].isnumeric():
        return await message.reply("<b>Masukkan input yang valid!</b>\n\nContoh: <code>/remove 91838299</code>")
    _, user_id = message.text.split()
    dbs._buyer[int(user_id)] = None
    save_data()
    await message.reply(f"<b><i>Pengguna {user_id} telah dihapus dari akses!</b></i>")

@on_msg(filters.command("update") & filters.user(OWNER_ID[0]))
async def update_bot(client, message):
    x = await message.reply("Updating...", quote=True)
    #subprocess.run(['git', 'pull', '-q'])
    await x.edit("Successfully updating, restart!")
    os.execl(sys.executable, sys.executable, "main.py")

@on_msg(filters.command("check") & filters.user(OWNER_ID))
async def check_exp():
    while True:
        totalbuyer = dbs._buyer
        waktu_sekarang = datetime.now()
        for buyer in totalbuyer:
            if not dbs._buyer[buyer]:
                continue
            selisih = waktu_sekarang - dbs._buyer[buyer]
            if selisih >= timedelta(minutes=1):
                try:
                    await bot.send_message(OWNER_ID[0], f"<b><i>{buyer} telah expired!</b></i>")
                    await bot.send_message(buyer, f"<b><i>Masa aktif bot anda telah habis, harap order ulang untuk menggunakannya!</b></i>")
                except:
                    pass
                dbs._buyer[buyer] = None
        await asyncio.sleep(600)


async def main():
    data_ = load_data()
    dbs._buyer = data_
    await bot.start()
    await check_exp()

if __name__ == "__main__":
    asyncio.get_event_loop_policy().get_event_loop().run_until_complete(main())
