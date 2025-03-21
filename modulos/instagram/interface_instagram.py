# Janel do Instagram
    # def instaloader_janela():
    #     """ Função para extrair o id do link do post
    #     A biblioteca Instaloader só recebe o id do post, caso envie o link completo o sistema para de funcionar"""
    #     def extrair_post_id(link):
    #         match = re.search(
    #             r"https://www.instagram.com/p/([A-Za-z0-9_-]+)", link)
    #         if match:
    #             return match.group(1)
    #         else:
    #             return link  # Caso o usuário tenha digitado apenas o ID diretamente

    #     """ Função para extrair o nome do perfil do usuário
    #     A biblioteca Instaloader só recebe o nome do perfil do usuário, caso envie o link completo o sistema para de funcionar """
    #     def extrair_nome_perfil(link):
    #         # Usamos regex para capturar o que está entre "instagram.com/" e o próximo "/"
    #         match = re.search(r"https://www.instagram.com/([^/]+)/?", link)
    #         if match:
    #             return match.group(1)
    #         else:
    #             return link  # Caso o usuário tenha digitado apenas o @ do usuário diretamente

    #     tk_instagram = tk.Toplevel(tk_custodia_tech)
    #     tk_instagram.iconbitmap(
    #         get_resource_path(icone_custodia))
    #     tk_instagram.title("Baixar Perfil Instagram")
    #     tk_instagram.resizable(False, False)
    #     tk_instagram.attributes('-fullscreen', False)

    #     window_width = 400
    #     window_height = 450

    #     screen_width = tk_instagram.winfo_screenwidth()
    #     screen_height = tk_instagram.winfo_screenheight()

    #     x = (screen_width // 2) - (window_width // 2)
    #     y = (screen_height // 2) - (window_height // 2)

    #     tk_instagram.geometry(f"{window_width}x{window_height}+{x}+{y}")

    #     lista_atividade_frame = ttk.LabelFrame(
    #         tk_instagram, text="Tipo de Coleta", bootstyle="primary")
    #     lista_atividade_frame.pack(pady=5, fill='both', expand=True)

    #     # Movendo a Label "Usuário" e o campo de entrada para dentro do frame
    #     label_username = tk.Label(lista_atividade_frame, text="Usuário:")
    #     label_username.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    #     entry_username = ttk.Entry(lista_atividade_frame, bootstyle="dark")
    #     entry_username.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    #     var_simplificada = tk.BooleanVar()
    #     var_periodo = tk.BooleanVar()
    #     var_individual = tk.BooleanVar()

    #     check_button_simplificada = ttk.Checkbutton(lista_atividade_frame, text="Coletar todos os posts",
    #                                                 variable=var_simplificada, style="info.Roundtoggle.Toolbutton", command=lambda: update_button_state(button))
    #     check_button_simplificada.grid(
    #         row=1, column=0, columnspan=2, padx=5, pady=10, sticky="w")

    #     check_button_periodo = ttk.Checkbutton(lista_atividade_frame, text="Coletar posts por Período",
    #                                            variable=var_periodo, style="info.Roundtoggle.Toolbutton", command=lambda: toggle_date_pickups())
    #     check_button_periodo.grid(
    #         row=2, column=0, columnspan=2, padx=5, pady=10, sticky="w")

    #     date_picker_inicial = DateEntry(
    #         lista_atividade_frame, bootstyle="primary")
    #     date_picker_inicial.grid(row=3, column=0, padx=5, pady=10, sticky="w")
    #     date_picker_inicial.configure(state="disabled")

    #     date_picker_final = DateEntry(
    #         lista_atividade_frame, bootstyle="primary")
    #     date_picker_final.grid(row=3, column=1, padx=5, pady=10, sticky="w")
    #     date_picker_final.configure(state="disabled")

    #     check_button_individual = ttk.Checkbutton(lista_atividade_frame, text="Coletar post individual", variable=var_individual,
    #                                               style="info.Roundtoggle.Toolbutton", command=lambda: update_button_individual(button))
    #     check_button_individual.grid(
    #         row=4, column=0, columnspan=2, padx=5, pady=10, sticky="w")

    #     label_text = "https://www.instagram.com/p/"
    #     label = ttk.Label(lista_atividade_frame, text=label_text)
    #     label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

    #     entry_post = ttk.Entry(lista_atividade_frame, bootstyle="dark")
    #     entry_post.grid(row=5, column=1, padx=5, pady=5, sticky="w")

    #     def toggle_date_pickups():
    #         if var_periodo.get():
    #             date_picker_inicial.configure(state="normal")
    #             date_picker_final.configure(state="normal")
    #             button.config(state=tk.NORMAL)
    #         else:
    #             date_picker_inicial.configure(state="disabled")
    #             date_picker_final.configure(state="disabled")
    #             button.config(state=tk.DISABLED)

    #     def update_button_state(button):
    #         if var_simplificada.get():
    #             entry_post.state(['disabled'])
    #             button.config(state=tk.NORMAL)
    #         else:
    #             entry_post.state(['!disabled'])
    #             button.config(state=tk.DISABLED)

    #     def update_button_individual(button):
    #         if var_individual.get():
    #             button.config(state=tk.NORMAL)
    #         else:
    #             button.config(state=tk.DISABLED)

    #     def atualizar_progress_bar(progress_bar, valor):
    #         progress_bar['value'] = valor
    #         progress_bar.update()  # Atualiza a interface gráfica

    #     def download_profile():
    #         username_bruto = entry_username.get()
    #         username = extrair_nome_perfil(username_bruto)
    #         directory = case_directory

    #         if not os.path.isdir(directory):
    #             label_status.config(text="Diretório inválido.")
    #             return

    #         if var_individual.get():

    #             atualizar_progress_bar(progress_bar, 30)

    #             L = instaloader.Instaloader()

    #             post_id_raw = entry_post.get()
    #             post_id = extrair_post_id(post_id_raw)

    #             save_directory = pathlib.Path(case_directory)

    #             post_directory = save_directory / post_id
    #             post_directory.mkdir(parents=True, exist_ok=True)

    #             L.dirname_pattern = str(post_directory)

    #             post = instaloader.Post.from_shortcode(L.context, post_id)

    #             L.download_post(post, target='')

    #             print(f'Postagem {post_id} baixada com sucesso em {
    #                   post_directory}')
    #             atualizar_progress_bar(progress_bar, 70)
    #             for tk_custodia_tech_dir, _, files in os.walk(post_directory):
    #                 for file_name in files:
    #                     file_path = os.path.join(tk_custodia_tech_dir, file_name)

    #                     # Compacta o arquivo
    #                     zip_file_path = file_path + '.zip'
    #                     with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
    #                         zip_file.write(file_path, file_name)

    #                     # Exclui o arquivo original
    #                     os.remove(file_path)

    #                     # Calcula o hash e os metadados do arquivo compactado
    #                     hashes = calculate_hash(zip_file_path, algorithms=[
    #                                             'md5', 'sha1', 'sha256'])
    #                     metadata = get_file_metadata(zip_file_path)

    #                     # Atualiza a lista com o nome do arquivo
    #                     file_data_instagram.append({
    #                         'perfil': post.owner_username,  # Nome do perfil do Instagram
    #                         'nome_do_arquivo': file_name + '.zip',
    #                         'hashes': hashes,
    #                         'metadata': metadata
    #                     })

    #                     # Imprime informações para verificação
    #                     print(f"Arquivo: {zip_file_path}")
    #                     print(f"Hashes: {hashes}")
    #                     print(f"Metadados: {metadata}")
    #                     print("-" * 40)
    #             atualizar_progress_bar(progress_bar, 100)

    #             # Exibe uma mensagem de sucesso
    #             messagebox.showinfo(
    #                 'Instagram', 'Post baixado e dados extraídos com sucesso!')

    #         if var_periodo.get():
    #             if not var_simplificada.get():  # Verifica se var_simplificada é False
    #                 try:
    #                     # Obtenha as datas como strings no formato dd/mm/yyyy
    #                     start_date_str = date_picker_inicial.entry.get()
    #                     end_date_str = date_picker_final.entry.get()

    #                     # Converta as strings para objetos datetime no formato dd/mm/yyyy
    #                     start_date = datetime.strptime(
    #                         start_date_str, "%d/%m/%Y")
    #                     end_date = datetime.strptime(end_date_str, "%d/%m/%Y")

    #                     # Adicione a hora "00:00:00" ao final das datas e formate-as para "yyyy-mm-dd HH:MM:SS"
    #                     start_date_str = start_date.strftime(
    #                         "%Y-%m-%d 00:00:00")
    #                     end_date_str = end_date.strftime("%Y-%m-%d 00:00:00")

    #                     # Exiba para verificar as datas
    #                     print(start_date_str)
    #                     print(end_date_str)
    #                     atualizar_progress_bar(progress_bar, 30)

    #                     # Chame o método adequado para fazer o download do Instagram por posts
    #                     instagram.download_instagram_por_periodo(
    #                         username, case_directory, start_date_str, end_date_str)
    #                     atualizar_progress_bar(progress_bar, 100)

    #                     # Diretório do perfil
    #                     profile_directory = os.path.join(case_directory, f"{(username)}_{
    #                                                      start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}")

    #                     # Percorre os arquivos baixados
    #                     for tk_custodia_tech_dir, _, files in os.walk(profile_directory):
    #                         for file_name in files:
    #                             file_path = os.path.join(tk_custodia_tech_dir, file_name)

    #                             # Compacta o arquivo
    #                             zip_file_path = file_path + '.zip'
    #                             with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
    #                                 zip_file.write(file_path, file_name)

    #                             os.remove(file_path)

    #                             # Calcula o hash e os metadados do arquivo compactado
    #                             hashes = calculate_hash(zip_file_path, algorithms=[
    #                                                     'md5', 'sha1', 'sha256'])
    #                             metadata = get_file_metadata(zip_file_path)

    #                             # Atualiza a lista com o nome do arquivo
    #                             file_data_instagram.append({
    #                                 'perfil': username,  # Nome do perfil do Instagram
    #                                 'nome_do_arquivo': file_name + '.zip',
    #                                 'hashes': hashes,
    #                                 'metadata': metadata
    #                             })

    #                             # Imprime informações para verificação
    #                             print(f"Arquivo: {zip_file_path}")
    #                             print(f"Hashes: {hashes}")
    #                             print(f"Metadados: {metadata}")
    #                             print("-" * 40)

    #                     messagebox.showinfo(
    #                         'Instagram', 'Posts baixados e dados extraídos com sucesso!')

    #                     # Gravação de log
    #                     registrar_acao(
    #                         "Posts do Instagram coletados por período",
    #                         f"Os posts do usuário {username} de {start_date_str} a {
    #                         end_date_str} foram coletados pelo usuário {usuario} na máquina {ip_local} e salvos no diretório {case_directory}"
    #                     )

    #                 except instagram.exceptions.ConnectionException as e:
    #                     label_status.config(text="Perfil não encontrado.")
    #                     messagebox.showerror(
    #                         'Instagram', 'Perfil não encontrado!')
    #                     tk_instagram.destroy()
    #                 except Exception as e:
    #                     label_status.config(text=f"Erro: {e}")
    #                     messagebox.showerror('Instagram', e)
    #                     tk_instagram.destroy()

    #         if var_simplificada.get():
    #             L = instaloader.Instaloader()

    #             L.dirname_pattern = os.path.join(directory, '{target}')

    #             try:
    #                 profile = instaloader.Profile.from_username(
    #                     L.context, username)
    #                 posts = list(profile.get_posts())
    #                 total_posts = len(posts)
    #                 progress_bar["maximum"] = total_posts

    #                 if total_posts == 0:
    #                     label_status.config(
    #                         text="Nenhum post encontrado no perfil.")
    #                     messagebox.showinfo(
    #                         'Instagram', 'Esta conta é privada ou nenhum dado foi encontrado.')
    #                     tk_instagram.destroy()
    #                     return

    #                 for index, post in enumerate(posts, 1):
    #                     L.download_post(post, target=profile.username)
    #                     progress_bar["value"] = index
    #                     label_status.config(
    #                         text=f"Baixando... ({index}/{total_posts})")
    #                     tk_instagram.update_idletasks()

    #                 label_status.config(text=f"Download do perfil {
    #                                     username} concluído!")
    #                 messagebox.showinfo(
    #                     'Instagram', 'Perfil baixado com sucesso!')
    #                 profile_directory = os.path.join(directory, username)
    #                 for tk_custodia_tech_dir, _, files in os.walk(profile_directory):
    #                     for file_name in files:
    #                         file_path = os.path.join(tk_custodia_tech_dir, file_name)

    #                         # Compacta o arquivo
    #                         zip_file_path = file_path + '.zip'
    #                         with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
    #                             zip_file.write(file_path, file_name)

    #                         os.remove(file_path)

    #                         # Calcula o hash e os metadados do arquivo compactado
    #                         hashes = calculate_hash(zip_file_path, algorithms=[
    #                                                 'md5', 'sha1', 'sha256'])
    #                         metadata = get_file_metadata(zip_file_path)

    #                         # Atualiza a lista com o nome do arquivo
    #                         file_data_instagram.append({
    #                             'perfil': username,  # Nome do perfil do Instagram
    #                             'nome_do_arquivo': file_name + '.zip',
    #                             'hashes': hashes,
    #                             'metadata': metadata
    #                         })

    #                         # Imprime informações para verificação
    #                         print(f"Arquivo: {zip_file_path}")
    #                         print(f"Hashes: {hashes}")
    #                         print(f"Metadados: {metadata}")
    #                         print("-" * 40)

                    # registrar_acao(
                    #     "Perfil do instagram coletado",
                    #     f"O perfil do usuario do instagram {username} foi coletado pelo usuario {
                    #     usuario} na maquina {ip_local} e salvo no diretorio {case_directory}"
                    # )
    #                 tk_instagram.destroy()

    #             except instagram.exceptions.ConnectionException as e:
    #                 label_status.config(text="Perfil não encontrado.")
    #                 messagebox.showerror('Instagram', 'Perfil não encontrado!')
    #                 tk_instagram.destroy()
    #             except Exception as e:
    #                 label_status.config(text=f"Erro: {e}")
    #                 messagebox.showerror('Instagram', e)
    #                 tk_instagram.destroy()

    #     progress_bar = ttk.Progressbar(
    #         tk_instagram, orient="horizontal", mode="determinate", length=200, bootstyle="warning-striped")
    #     progress_bar.pack(pady=10)

    #     button = tk.Button(tk_instagram, text="Baixar",
    #                        command=download_profile, state=tk.DISABLED)
    #     button.pack(pady=10)

    #     label_status = tk.Label(tk_instagram, text="")
    #     label_status.pack(pady=10)

    #     tk_instagram.transient(tk_custodia_tech)
    #     tk_instagram.grab_set()
    #     tk_custodia_tech.wait_window(tk_instagram)