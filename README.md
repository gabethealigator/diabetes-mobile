# Diabetes Mobile

Um aplicativo móvel para gerenciamento e monitoramento de pacientes com diabetes.

## Descrição

Diabetes Mobile é uma aplicação desenvolvida com Kivy/KivyMD que permite aos profissionais de saúde ou pacientes monitorar níveis de glicose, medicamentos e informações gerais de saúde. O aplicativo oferece uma interface amigável para:

- Cadastrar e gerenciar pacientes
- Registrar e visualizar medições de glicose
- Acompanhar medicamentos prescritos
- Visualizar gráficos de progresso dos níveis de glicose

## Tecnologias Utilizadas

- Python
- Kivy/KivyMD (interface gráfica)
- MySQL (banco de dados)
- Matplotlib (visualização de dados)
- Pandas (manipulação de dados)

## Requisitos

```
kivy==2.3.0
kivy-garden==0.1.5
kivy-garden.matplotlib==0.1.1.dev0
kivymd==1.2.0
matplotlib==3.9.0
mysql-connector==2.2.9
pandas==2.2.2
```

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/diabetes-mobile.git
cd diabetes-mobile
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Configure o banco de dados MySQL:
   - Crie um banco de dados chamado "diabetes"
   - Execute o script SQL fornecido:
   ```
   mysql -u root -p < diabetes.sql
   ```

4. Configure as credenciais do banco de dados no arquivo `main.py`:
```python
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'diabetes'
```

## Uso

Execute o aplicativo:
```
python main.py
```

### Funcionalidades

- **Tela Inicial**: Visão geral da saúde do paciente
- **Controle**: Gerenciamento de medições e dados
- **Diabetes**: Monitoramento de níveis de glicose com visualização gráfica
- **Medicamentos**: Gerenciamento de medicamentos prescritos

## Estrutura do Banco de Dados

O aplicativo utiliza três tabelas principais:

1. **paciente**: Armazena informações dos pacientes (nome, idade, sexo, etc.)
2. **controle_dt**: Registra medições de glicose e outros parâmetros de saúde
3. **medicamento**: Armazena informações sobre medicamentos prescritos

## Licença

Este projeto está licenciado sob a licença incluída no arquivo LICENSE.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests. 
