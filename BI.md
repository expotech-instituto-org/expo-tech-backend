

## Passo 0:
Descubra o número do seu grupo

| Group Number | Group Name   |
|--------------|-------------|
| 1            | NUTRIA      |
| 2            | SANCARAN    |
| 3            | AION        |
| 4            | SINARA      |
| 5            | ZETA        |
| 6            | ESSENTIA    |
| 7            | YBYRATECH   |
| 8            | IARA        |
| 9            | CODCOZ      |
| 10           | INVOLUCRE   |
| 11           | I_GESTA     |
| 12           | FROTA VIVA  |
| 13           | KRONOS      |
| 14           | SCANEIA     |
| 15           | INFOONE     |
| 16           | TIMELEAN    |
| 17           | VIREYA      |
| 18           | ECOFACTORY  |
| 19           | MAGNA       |
| 20           | NEOTECH     |
| 21           | EI_TRUCK    |
| 22           | CONTABACO   |
| 23           | PURPURA     |
| 24           | SIMBIA      |



## Passo 1:
Faça login no sistema

### Reqisição:
```
curl -X 'POST' \
 'https://expo-tech-backend.onrender.com/users/login' \
 -H 'accept: application/json' \
 -H 'Content-Type: application/x-www-form-urlencoded' \
 -d 'username=expositor_project-uuid-<NÚMERO-DO-MAPA>@example.com&password=senha123'
```
### Resposta:
```
{
  "access_token": "string",
  "token_type": "string"
}
```

## Passo 2:
Busque as reviews do seu projeto

### Reqisição:
```
curl -X 'GET' \
 'https://expo-tech-backend.onrender.com/reviews/project/' \
 -H 'accept: application/json' \
 -H 'Authorization: Bearer <TOKEN-OBTIDO-NO-PASSO-1>'
```
### Resposta:
```
[
  {
    "id": "review-uuid-1-1",
    "grades": [
      {
        "name": "Apresentação do projeto",
        "score": 4,
        "weight": 0.25
      },
      {
        "name": "Solução desenvolvida",
        "score": 4,
        "weight": 0.25
      },
      {
        "name": "Apresentação do stand",
        "score": 5,
        "weight": 0.25
      },
      {
        "name": "Ideia usada para resolver o problema",
        "score": 4,
        "weight": 0.25
      }
    ],
    "project_id": "project-uuid-1"
  }
]
```

## Exemplo em python

```python
import requests
import pandas as pd

# Passo 1: Login
numero_mapa = 1
login_url = "https://expo-tech-backend.onrender.com/users/login"
login_data = {
    "username": f"expositor_project-uuid-{numero_mapa}@example.com",
    "password": "senha123"
}
login_headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}
response = requests.post(login_url, data=login_data, headers=login_headers)
token = response.json().get("access_token")

# Passo 2: Buscar reviews do projeto
if token:
    reviews_url = "https://expo-tech-backend.onrender.com/reviews/project/"
    reviews_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    reviews_response = requests.get(reviews_url, headers=reviews_headers)
    data = reviews_response.json()
    
    # Passo 3: Transformar dados em DataFrame para uso do BI
    
    all_grades = []
    for review in data:
        for grade in review["grades"]:
            all_grades.append({
                "review_id": review["_id"],
                "grade_name": grade["name"],
                "score": grade["score"],
                "weight": grade["weight"],
            })
    grades_df = pd.DataFrame(all_grades)
    
else:
    print("Erro ao obter token de autenticação.")