import uuid
from project import ProjectModel, UserExpositor  # assumindo que está nesse arquivo
from user import UserModel

# 1️⃣ Criando um usuário expositor de teste
user_expositor = UserExpositor(
    id="user123",
    name="Alice",
    _class="Speaker"
)

# 2️⃣ Criando um projeto de teste
project = ProjectModel(
    _id=str(uuid.uuid4()),  # usando alias
    name="Tech Corp",
    company_name="Tech Corporation",
    description="A tech company specializing in AI",
    coordinates=123,
    exhibition_id="exh_456",
    expositors=[user_expositor],
    images=["img1.png", "img2.png"],
    logo="logo.png"
)

# 3️⃣ Imprimindo o objeto Python
print("Objeto Python:")
print(project)

# 4️⃣ Imprimindo o JSON com aliases
print("\nJSON com aliases:")
print(project.model_dump(by_alias=True))

# 5️⃣ Testando validação (isto deve falhar)
try:
    invalid_project = ProjectModel(
        _id=str(uuid.uuid4()),
        name="Invalid Project",
        company_name="Invalid Co",
        description="Test invalid coordinates",
        coordinates="not an int",  # tipo errado
        exhibition_id="exh_999",
        expositors=[user_expositor],
        images=["img.png"],
        logo="logo.png"
    )
except Exception as e:
    print("\nErro de validação capturado:")
    print(e)
