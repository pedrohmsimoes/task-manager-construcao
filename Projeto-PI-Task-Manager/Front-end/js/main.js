document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const idObra = params.get('id');

  // === DADOS DA OBRA (Cliente, Título, Status) ===
  if (idObra) {
    fetch(`http://localhost:5000/obras/${idObra}`)
  .then(res => res.json())
  .then(data => {
    if (idObra) {
      fetch(`http://localhost:5000/obras/${idObra}`)
        .then(res => res.json())
        .then(data => {
          if (data.erro) {
            console.error('Erro:', data.erro);
          } else {
            // Preenche os campos no Admin
            const clienteNomeEl = document.getElementById('cliente_nome');
            const tituloEl = document.getElementById('titulo');
            const statusEl = document.getElementById('status');
            const orcamentoEl = document.getElementById('orcamentoExibido');
            
    
            if (clienteNomeEl) clienteNomeEl.textContent = data.cliente_nome || 'Não informado';
            if (tituloEl) tituloEl.textContent = data.titulo || 'Não informado';
            if (statusEl) statusEl.textContent = data.status || 'Não informado';
            if (orcamentoEl) orcamentoEl.textContent = data.orcamento_total 
              ? parseFloat(data.orcamento_total).toLocaleString('pt-BR', { minimumFractionDigits: 2 })
              : '0,00';
          }
        })
        .catch(err => {
          console.error('Erro ao carregar dados da obra:', err);
        });
    }
    if (idObra) {
      fetch(`http://localhost:5000/obras/${idObra}`)
        .then(res => res.json())
        .then(data => {
          if (data.erro) {
            console.error('Erro:', data.erro);
          } else {
            document.getElementById('id_obra').textContent = data.id || 'Não informado';
            document.getElementById('cliente_nome').textContent = data.cliente_nome || 'Não informado';
            document.getElementById('titulo').textContent = data.titulo || 'Não informado';
            document.getElementById('status').textContent = data.status || 'Não informado';
            document.getElementById('orcamentoExibido').textContent = data.orcamento_total 
              ? parseFloat(data.orcamento_total).toLocaleString('pt-BR', { minimumFractionDigits: 2 })
              : '0,00';
          }
        })
        .catch(err => console.error('Erro ao carregar dados:', err));
      // Renderizar gráfico circular da meta de investimento
      new Chart(document.getElementById('graficoMeta'), {
        type: 'doughnut',
        data: {
          labels: ['Gasto (%)', 'Restante (%)'],
          datasets: [{
            data: [data.percentual_gasto, 100 - data.percentual_gasto],
            backgroundColor: ['#ff7a00', '#e0e0e0']
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      });

      // Mostrar o texto de comparação de valores
      document.getElementById('infoGasto').innerHTML = `
        Gasto Total: R$ ${parseFloat(data.total_gasto).toFixed(2)} /
        Orçamento Total: R$ ${parseFloat(data.orcamento_total || 0).toFixed(2)}
      `;
    }
  });
  }

  // === GALERIA DE FOTOS ===
  if (document.getElementById('galeria') && idObra) {
    fetch(`http://localhost:5000/obras/${idObra}/fotos`)
    .then(res => res.json())
    .then(data => {
    const galeria = document.getElementById('galeria');
    galeria.innerHTML = '';

    if (data.fotos && data.fotos.length > 0) {
      data.fotos.forEach(foto => {
        const container = document.createElement('div');
        container.style.position = 'relative';
        container.style.display = 'inline-block';
        container.style.margin = '10px';

        const img = document.createElement('img');
        img.src = `http://localhost:5000${foto}`;
        img.style.width = '200px';
        img.style.borderRadius = '5px';

        // Botão de excluir
        const btnExcluir = document.createElement('button');
        btnExcluir.textContent = '❌';
        btnExcluir.title = 'Excluir Foto';
        btnExcluir.style.position = 'absolute';
        btnExcluir.style.top = '5px';
        btnExcluir.style.right = '5px';
        btnExcluir.style.background = '#ff4d4d';
        btnExcluir.style.color = 'white';
        btnExcluir.style.border = 'none';
        btnExcluir.style.borderRadius = '50%';
        btnExcluir.style.width = '24px';
        btnExcluir.style.height = '24px';
        btnExcluir.style.cursor = 'pointer';

        const nomeArquivo = foto.split(`obra_${idObra}_`)[1];

        btnExcluir.addEventListener('click', () => {
          if (confirm('Deseja excluir esta foto?')) {
            fetch(`http://localhost:5000/obras/${idObra}/fotos/${nomeArquivo}`, {
              method: 'DELETE'
            })
            .then(res => res.json())
            .then(resp => {
              alert(resp.msg || resp.erro);
              container.remove();
            });
          }
        });

        container.appendChild(img);
        container.appendChild(btnExcluir);
        galeria.appendChild(container);
      });
    } else {
      galeria.textContent = 'Nenhuma foto disponível.';
    }
  })
  .catch(err => {
    document.getElementById('galeria').textContent = `Erro ao carregar fotos: ${err}`;
  });

  }

  // === UPLOAD DE FOTOS ===
  const uploadBtn = document.getElementById('fotoObra');
  if (uploadBtn) {
    document.querySelector('button[onclick="uploadFotos()"]')?.addEventListener('click', () => {
      const fotos = uploadBtn.files;
      const formData = new FormData();
      for (let i = 0; i < fotos.length; i++) {
        formData.append('fotos', fotos[i]);
      }

      fetch(`http://localhost:5000/obras/${idObra}/fotos`, {
        method: 'POST',
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById('msgFoto').textContent = data.msg || data.erro;
        })
        .catch(err => {
          document.getElementById('msgFoto').textContent = `Erro ao enviar fotos: ${err}`;
        });
    });
  }

  // === ADICIONAR MATERIAL ===
  const formMaterial = document.getElementById('formMaterial');
  if (formMaterial && idObra) {
    formMaterial.addEventListener('submit', e => {
      e.preventDefault();
      const body = {
        nome: document.getElementById('nome_material').value,
        quantidade: document.getElementById('quantidade').value,
        custo: document.getElementById('custo').value
      };

      fetch(`http://localhost:5000/obras/${idObra}/materiais`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
        .then(res => res.json())
        .then(resp => {
          document.getElementById('msgMaterial').textContent = resp.msg || resp.erro;
          formMaterial.reset();
        });
    });
  }

  // === GRÁFICO DE GASTOS POR MATERIAL ===
  if (document.getElementById('graficoMateriais') && idObra) {
    fetch(`http://localhost:5000/obras/${idObra}/materiais`)
      .then(res => res.json())
      .then(data => {
        const nomes = data.map(m => m.nome || m.nome_material);
        const valores = data.map(m => m.total || (m.quantidade * m.custo));

        new Chart(document.getElementById('graficoMateriais'), {
          type: 'bar',
          data: {
            labels: nomes,
            datasets: [{
              label: 'Gasto por Material (R$)',
              data: valores,
              backgroundColor: '#ff7a00'
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: { beginAtZero: true }
            }
          }
        });
      });
  }
});

function mostrarFormularioOrcamento() {
  document.getElementById('formOrcamento').style.display = 'block';
}

document.addEventListener('DOMContentLoaded', () => {
  const idObra = new URLSearchParams(window.location.search).get('id');
  const formOrc = document.getElementById('formOrcamento');

  if (formOrc && idObra) {
    formOrc.addEventListener('submit', (e) => {
      e.preventDefault();
      const novoValor = document.getElementById('novo_orcamento').value;

      fetch(`http://localhost:5000/obras/${idObra}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ orcamento_total: novoValor }) // Atualiza só orçamento
      })
      .then(res => res.json())
      .then(resp => {
        document.getElementById('msgOrcamento').textContent = resp.msg || resp.erro;
        document.getElementById('orcamentoExibido').textContent = parseFloat(novoValor).toFixed(2);
        formOrc.reset();
        formOrc.style.display = 'none';
      });
    });
  }
});


document.getElementById('formStatus').addEventListener('submit', (e) => {
  e.preventDefault();

  const idObra = new URLSearchParams(window.location.search).get('id');
  const novoStatus = document.getElementById('novo_status').value;

  fetch(`http://localhost:5000/obras/${idObra}/status`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status: novoStatus })
  })
  .then(res => res.json())
  .then(data => {
    if (data.sucesso) {
      document.getElementById('status').innerText = novoStatus;
      document.getElementById('msgStatus').innerText = 'Status atualizado com sucesso!';
      document.getElementById('msgStatus').style.color = 'green';
    } else {
      document.getElementById('msgStatus').innerText = 'Erro ao atualizar o status.';
      document.getElementById('msgStatus').style.color = 'red';
    }
  })
  .catch(err => {
    console.error(err);
    document.getElementById('msgStatus').innerText = 'Erro na conexão com o servidor.';
    document.getElementById('msgStatus').style.color = 'red';
  });
});

