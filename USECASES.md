# PetLar - Relatório de Casos de Uso

Este documento lista todos os casos de uso de requisitos funcionais presentes no sistema PetLar, indicando quais perfis de usuário podem executar cada caso de uso.

---

## Perfis de Usuário

O sistema possui **3 perfis de usuário**:

| Perfil | Descrição |
|--------|-----------|
| **Administrador** | Administrador do sistema com acesso total |
| **Abrigo** | Funcionário/responsável por abrigo de animais |
| **Adotante** | Usuário interessado em adotar animais |

---

## Módulo 1: Autenticação e Registro

| ID | Caso de Uso | Administrador | Abrigo | Adotante | Público |
|----|-------------|:-------------:|:------:|:--------:|:-------:|
| UC-AUTH-001 | Cadastrar novo usuário | - | X | X | X |
| UC-AUTH-002 | Realizar login | X | X | X | - |
| UC-AUTH-003 | Realizar logout | X | X | X | - |
| UC-AUTH-004 | Solicitar recuperação de senha | X | X | X | X |
| UC-AUTH-005 | Redefinir senha com token | X | X | X | X |

---

## Módulo 2: Gerenciamento de Perfil do Usuário

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-PROFILE-001 | Visualizar próprio perfil | X | X | X |
| UC-PROFILE-002 | Editar próprio perfil | X | X | X |
| UC-PROFILE-003 | Alterar própria senha | X | X | X |
| UC-PROFILE-004 | Enviar foto de perfil | X | X | X |

---

## Módulo 3: Gerenciamento de Endereço

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-ADDRESS-001 | Visualizar próprio endereço | - | X | X |
| UC-ADDRESS-002 | Cadastrar endereço | - | X | X |
| UC-ADDRESS-003 | Editar endereço | - | X | X |
| UC-ADDRESS-004 | Excluir endereço | - | X | X |

---

## Módulo 4: Administração de Usuários

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-ADMIN-USR-001 | Listar todos os usuários | X | - | - |
| UC-ADMIN-USR-002 | Cadastrar usuário | X | - | - |
| UC-ADMIN-USR-003 | Editar usuário | X | - | - |
| UC-ADMIN-USR-004 | Excluir usuário | X | - | - |

---

## Módulo 5: Gerenciamento de Animais

### 5.1 Visualização Pública de Animais

| ID | Caso de Uso | Administrador | Abrigo | Adotante | Público |
|----|-------------|:-------------:|:------:|:--------:|:-------:|
| UC-ANIMAL-001 | Visualizar lista de animais disponíveis | X | X | X | X |
| UC-ANIMAL-002 | Visualizar detalhes do animal | X | X | X | X |
| UC-ANIMAL-003 | Curtir/favoritar animal | - | - | X | - |

### 5.2 Administração de Animais (Admin)

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-ANIMAL-004 | Cadastrar animal (Admin) | X | - | - |
| UC-ANIMAL-005 | Visualizar animal com detalhes completos (Admin) | X | - | - |
| UC-ANIMAL-006 | Editar animal (Admin) | X | - | - |
| UC-ANIMAL-007 | Alterar status do animal (Admin) | X | - | - |

### 5.3 Gerenciamento de Animais pelo Abrigo

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-ANIMAL-008 | Listar animais do próprio abrigo | - | X | - |
| UC-ANIMAL-009 | Cadastrar animal no abrigo | - | X | - |
| UC-ANIMAL-010 | Editar animal do próprio abrigo | - | X | - |
| UC-ANIMAL-011 | Visualizar detalhes do animal do abrigo | - | X | - |
| UC-ANIMAL-012 | Excluir animal do abrigo | - | X | - |
| UC-ANIMAL-013 | Visualizar animais reservados | - | X | - |
| UC-ANIMAL-014 | Concluir adoção de animal | - | X | - |
| UC-ANIMAL-015 | Cancelar reserva de animal | - | X | - |

---

## Módulo 6: Adoção e Solicitações

### 6.1 Funcionalidades do Adotante

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-ADOPT-001 | Reservar animal para adoção | - | - | X |

### 6.2 Administração de Solicitações

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-ADOPT-002 | Listar solicitações de adoção | X | - | - |
| UC-ADOPT-003 | Visualizar detalhes da solicitação | X | - | - |
| UC-ADOPT-004 | Aprovar solicitação de adoção | X | - | - |
| UC-ADOPT-005 | Rejeitar solicitação de adoção | X | - | - |
| UC-ADOPT-006 | Cancelar solicitação de adoção | X | - | - |

---

## Módulo 7: Gerenciamento de Adotantes

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-ADOTANT-001 | Listar todos os adotantes | X | - | - |
| UC-ADOTANT-002 | Visualizar perfil do adotante | X | - | - |
| UC-ADOTANT-003 | Editar informações do adotante | X | - | - |

---

## Módulo 8: Gerenciamento de Abrigos

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-SHELTER-001 | Listar todos os abrigos | X | - | - |

---

## Módulo 9: Gerenciamento de Espécies e Raças

### 9.1 Espécies

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-SPECIES-001 | Listar espécies | X | - | - |
| UC-SPECIES-002 | Cadastrar espécie | X | - | - |
| UC-SPECIES-003 | Editar espécie | X | - | - |
| UC-SPECIES-004 | Excluir espécie | X | - | - |

### 9.2 Raças

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-BREED-001 | Listar raças | X | - | - |
| UC-BREED-002 | Cadastrar raça | X | - | - |
| UC-BREED-003 | Editar raça | X | - | - |
| UC-BREED-004 | Excluir raça | X | - | - |

---

## Módulo 10: Sistema de Chamados (Suporte)

### 10.1 Gerenciamento de Chamados pelo Usuário

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-TICKET-001 | Abrir chamado de suporte | X | X | X |
| UC-TICKET-002 | Listar próprios chamados | X | X | X |
| UC-TICKET-003 | Visualizar detalhes do chamado | X | X | X |
| UC-TICKET-004 | Responder ao próprio chamado | X | X | X |
| UC-TICKET-005 | Excluir próprio chamado | X | X | X |

### 10.2 Administração de Chamados

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-TICKET-006 | Listar todos os chamados | X | - | - |
| UC-TICKET-007 | Responder chamado de usuário | X | - | - |
| UC-TICKET-008 | Fechar chamado | X | - | - |
| UC-TICKET-009 | Reabrir chamado | X | - | - |

---

## Módulo 11: Chat em Tempo Real

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-CHAT-001 | Criar sala de chat | X | X | X |
| UC-CHAT-002 | Listar conversas | X | X | X |
| UC-CHAT-003 | Receber mensagens em tempo real | X | X | X |
| UC-CHAT-004 | Enviar mensagem | X | X | X |
| UC-CHAT-005 | Recuperar histórico de mensagens | X | X | X |
| UC-CHAT-006 | Marcar mensagens como lidas | X | X | X |
| UC-CHAT-007 | Buscar usuários para conversar | X | X | X |
| UC-CHAT-008 | Obter contagem de mensagens não lidas | X | X | X |

---

## Módulo 12: Configurações do Sistema

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-CONFIG-001 | Visualizar configurações do sistema | X | - | - |
| UC-CONFIG-002 | Atualizar configurações em lote | X | - | - |
| UC-CONFIG-003 | Alterar tema do sistema | X | - | - |
| UC-CONFIG-004 | Visualizar log de auditoria | X | - | - |

---

## Módulo 13: Backup e Recuperação do Banco de Dados

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-BACKUP-001 | Listar backups disponíveis | X | - | - |
| UC-BACKUP-002 | Criar backup do banco de dados | X | - | - |
| UC-BACKUP-003 | Restaurar backup | X | - | - |
| UC-BACKUP-004 | Excluir backup | X | - | - |
| UC-BACKUP-005 | Baixar arquivo de backup | X | - | - |

---

## Módulo 14: Gerenciamento de Curtidas

| ID | Caso de Uso | Administrador | Abrigo | Adotante |
|----|-------------|:-------------:|:------:|:--------:|
| UC-LIKE-001 | Listar todas as curtidas | X | - | - |
| UC-LIKE-002 | Cadastrar curtida | X | - | - |
| UC-LIKE-003 | Editar curtida | X | - | - |
| UC-LIKE-004 | Excluir curtida | X | - | - |

---

## Módulo 15: Páginas Públicas de Informação

| ID | Caso de Uso | Administrador | Abrigo | Adotante | Público |
|----|-------------|:-------------:|:------:|:--------:|:-------:|
| UC-PUBLIC-001 | Acessar página inicial | X | X | X | X |
| UC-PUBLIC-002 | Acessar página "Sobre" | X | X | X | X |

---

## Resumo por Perfil

### Administrador (45 casos de uso)
- Acesso total ao sistema
- Gerenciamento completo de usuários, animais, espécies, raças
- Administração de solicitações de adoção
- Configurações do sistema
- Backup e recuperação de dados
- Auditoria do sistema

### Abrigo (25 casos de uso)
- Gerenciamento de perfil e endereço próprio
- Cadastro e gerenciamento de animais do próprio abrigo
- Conclusão de adoções
- Sistema de chamados
- Chat em tempo real
- Visualização de animais públicos

### Adotante (20 casos de uso)
- Gerenciamento de perfil e endereço próprio
- Navegação e visualização de animais
- Reserva de animais para adoção
- Curtir/favoritar animais
- Sistema de chamados
- Chat em tempo real

### Público/Não autenticado (7 casos de uso)
- Cadastro de novo usuário
- Recuperação de senha
- Visualização de animais disponíveis
- Páginas informativas (home, sobre)

---

## Matriz de Acesso Resumida

| Funcionalidade | Admin | Abrigo | Adotante | Público |
|----------------|:-----:|:------:|:--------:|:-------:|
| Autenticação | X | X | X | X |
| Perfil próprio | X | X | X | - |
| Endereço próprio | - | X | X | - |
| Gerenciar usuários | X | - | - | - |
| Navegar animais | X | X | X | X |
| Cadastrar animais | X | X | - | - |
| Editar animais | X | X (próprios) | - | - |
| Reservar animal | - | - | X | - |
| Curtir animal | - | - | X | - |
| Gerenciar adoções | X | X (concluir) | - | - |
| Gerenciar espécies/raças | X | - | - | - |
| Chamados | X | X | X | - |
| Chat | X | X | X | - |
| Configurações | X | - | - | - |
| Backups | X | - | - | - |
| Auditoria | X | - | - | - |
