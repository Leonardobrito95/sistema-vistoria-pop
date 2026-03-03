// Validação e Acumulação de fotos (Câmera + Galeria)
document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('.photo-input');
    const finalInput = document.getElementById('final_upload_input');
    const photoCounter = document.getElementById('photo-counter');
    const fileListDisplay = document.getElementById('file-list-display');
    const btnClean = document.getElementById('btn-clean-photos');
    const form = document.querySelector('form.needs-validation');

    if (inputs.length === 0 || !finalInput) return;

    // Array global para armazenar os arquivos File selecionados
    let globalFiles = [];

    function updatePhotoStatus() {
        let totalFiles = globalFiles.length;
        let fileNames = [];

        globalFiles.forEach(file => {
            fileNames.push(`📸 ${file.name}`);
        });

        // Atualiza display da lista interativa
        if (fileNames.length > 0) {
            fileListDisplay.innerHTML = fileNames.join('<br>');
            if (btnClean) btnClean.classList.remove('d-none');
        } else {
            fileListDisplay.innerHTML = 'Nenhuma foto selecionada';
            if (btnClean) btnClean.classList.add('d-none');
        }

        // Constrói um objeto DataTransfer do zero para jogar no finalInput
        try {
            const dt = new DataTransfer();
            globalFiles.forEach(f => dt.items.add(f));
            finalInput.files = dt.files;
            console.log("DataTransfer populado com sucesso. Total:", dt.files.length);
        } catch (err) {
            console.error("DataTransfer não suportado pelo navegador nativo:", err);
        }

        // Atualiza contador e badge colorida
        if (photoCounter) {
            let message = '';
            let alertClass = '';

            if (totalFiles === 0) {
                photoCounter.innerHTML = '';
                return;
            }

            if (totalFiles >= 3 && totalFiles <= 6) {
                alertClass = 'alert-success';
                message = `✓ ${totalFiles} foto(s) prontas (Limite: 3 a 6)`;
            } else if (totalFiles > 6) {
                alertClass = 'alert-danger';
                message = `❌ Excesso: ${totalFiles} fotos (Máximo: 6)`;
            } else {
                alertClass = 'alert-warning';
                message = `⚠️ ${totalFiles} foto(s) (Faltam ${3 - totalFiles} para o mínimo)`;
            }

            photoCounter.innerHTML = `<div class="alert ${alertClass} py-2 mb-0 fw-bold">${message}</div>`;
        }
    }

    // Escutamos mudanças de 'Adição' (Câmera ou Galeria)
    inputs.forEach(input => {
        input.addEventListener('change', function (e) {
            try {
                if (!e.target.files || e.target.files.length === 0) {
                    console.warn("Change disparado, mas nenhum arquivo retornado pelo SO.");
                    return;
                }

                const newFiles = Array.from(e.target.files);
                let adicionou = false;

                // Filtra apenas os permitidos
                newFiles.forEach(file => {
                    if (file.size > 10 * 1024 * 1024) {
                        alert(`O arquivo "${file.name}" é muito grande! (Máx: 10MB)`);
                    } else {
                        // Verifica se arquivo já não está na lista global pro mesmo nome/tamanho (evita duplo clique acidental)
                        const exists = globalFiles.find(f => f.name === file.name && f.size === file.size);
                        if (!exists) {
                            globalFiles.push(file);
                            adicionou = true;
                        }
                    }
                });

                // Atualiza a tela e recria o DataTransfer somente se algo novo entrou
                if (adicionou) {
                    updatePhotoStatus();
                }

                // Tenta limpar o input original para permitir selecionar a mesma foto de novo. 
                // Coloquei em try/catch pq alguns webviews crasham ao fazer isso.
                try {
                    e.target.value = '';
                } catch (e) { }

            } catch (err) {
                alert('Erro na leitura da imagem: ' + err.message);
                console.error(err);
            }
        });
    });

    // Botão de Limpar (Zera tudo)
    if (btnClean) {
        btnClean.addEventListener('click', function () {
            globalFiles = []; // Reinicia o acumulador zerado
            updatePhotoStatus();
        });
    }

    // Validação no Submit e Envio via AJAX (Para driblar bloqueio de arquivos do Android/iOS e unificar validações)
    if (form) {
        form.addEventListener('submit', async function (event) {
            event.preventDefault(); // Impede o envio nativo do navegador SEMPRE (vamos enviar por fetch)
            event.stopPropagation();

            // 1) Validação de Checkboxes
            let formIsValid = true;
            const checkboxGroups = [
                { name: 'limpeza', groupElementId: 'limpeza-group', friendlyName: 'Limpeza e Organização' },
                { name: 'ar_condicionado', groupElementId: 'ar_condicionado-group', friendlyName: 'Funcionamento Ar Condicionado' },
                { name: 'gerador', groupElementId: 'gerador-group', friendlyName: 'Gerador' },
                { name: 'baterias', groupElementId: 'baterias-group', friendlyName: 'Banco de Baterias' },
                { name: 'rede_eletrica', groupElementId: 'rede_eletrica-group', friendlyName: 'Rede Elétrica' },
                { name: 'retificadoras', groupElementId: 'retificadoras-group', friendlyName: 'Retificadoras -48v' }
            ];

            // Tenta validar grupos de checkbox que existem na tela
            checkboxGroups.forEach(group => {
                const groupEl = document.getElementById(group.groupElementId);
                if (groupEl) { // Só valida se a área existe na tela (para não quebrar em formulários adaptados futuramente)
                    const checkboxes = document.querySelectorAll(`input[name="${group.name}"]:checked`);
                    if (checkboxes.length === 0) {
                        formIsValid = false;
                        alert(`Por favor, selecione pelo menos uma opção em "${group.friendlyName}".`);
                        groupEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            });

            if (!formIsValid) return false;

            // 2) Validação de Fotos
            let totalFiles = globalFiles.length;

            if (totalFiles < 3 || totalFiles > 6) {
                let msg = '';
                if (totalFiles > 6) {
                    msg = `Você tem ${totalFiles} fotos. O limite máximo é 6 fotos. Remova ${totalFiles - 6} foto(s) limpando a seleção e enviando de novo.`;
                } else {
                    msg = `Você adicionou ${totalFiles} foto(s). São necessárias pelo menos 3. Por favor, adicione mais ${3 - totalFiles} foto(s).`;
                }

                alert('⚠️ ATENÇÃO: FOTOS INCOMPLETAS\n\n' + msg);
                if (photoCounter) photoCounter.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return false;
            }

            // 3) Se tudo passou na validação, preparamos o envio AJAX Oculto
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Salvar';

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando arquivos...';
            }

            try {
                // Coleta todos os campos de texto, checkboxes do formulário nativamente
                const formData = new FormData(form);

                // Remove qualquer rastro dos inputs de arquivo originais para não sobrescrever
                formData.delete('fotos[]');
                formData.delete('fotos_camera[]');
                formData.delete('fotos_galeria[]');

                // Injeta manualmente as fotos limpinhas armazenadas no acumulador do JS
                globalFiles.forEach(file => {
                    formData.append('fotos[]', file);
                });

                // Envia para o Flask
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    redirect: 'follow'
                });

                if (response.ok) {
                    // O Flask manda um Redirect (302) de volta para o Dashboard quando salva. 
                    // O Fetch segue o redirect e o response.url apontará para o destino final!
                    window.location.href = response.url;
                } else {
                    // Se o servidor retornar 400 ou 500 (Erro de validação back-end)
                    const htmlResponse = await response.text();
                    document.open();
                    document.write(htmlResponse);
                    document.close();
                }

            } catch (error) {
                alert('Erro de rede ao salvar os dados. Tente novamente: ' + error.message);
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            }
        });
    }
});
