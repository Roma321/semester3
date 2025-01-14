import os

import seaborn as sns
import torch
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import matplotlib.pyplot as plt

# Загрузка данных из файлов
def load_data_from_folder(folder, label):
    texts = []
    labels = []
    for filename in os.listdir(folder)[:1000]:
        if filename.endswith('.txt'):
            with open(os.path.join(folder, filename), 'r', encoding='utf-8') as file:
                texts.append(file.read())
                labels.append(label)
    return texts, labels

# Загрузка данных
correct_texts, correct_labels = load_data_from_folder('correct', 1)  # класс 1
not_correct_texts, not_correct_labels = load_data_from_folder('not_correct', 0)  # класс 2

# Объединение данных
texts = correct_texts + not_correct_texts
labels = correct_labels + not_correct_labels

# Создание DataFrame
data = pd.DataFrame({'text': texts, 'label': labels})

# Разделение на обучающую и тестовую выборки
train_texts, test_texts, train_labels, test_labels = train_test_split(data['text'], data['label'], test_size=0.2, random_state=42)

# Загрузка токенизатора BERT для русского языка
tokenizer = BertTokenizer.from_pretrained('DeepPavlov/rubert-base-cased')

# Токенизация
train_encodings = tokenizer(list(train_texts), truncation=True, padding=True, max_length=512)
test_encodings = tokenizer(list(test_texts), truncation=True, padding=True, max_length=512)

# Преобразование данных в формат для PyTorch
class TextDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = TextDataset(train_encodings, train_labels.tolist())
test_dataset = TextDataset(test_encodings, test_labels.tolist())

# Загрузка модели BERT для русского языка
model = BertForSequenceClassification.from_pretrained('DeepPavlov/rubert-base-cased', num_labels=2)

# Определение аргументов обучения
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=10,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

# Обучение модели
trainer.train()

# Оценка модели
# trainer.evaluate()

# Оценка модели
outputs = trainer.predict(test_dataset)
predictions = torch.argmax(torch.tensor(outputs.predictions), dim=1)
labels = torch.tensor(test_labels.tolist())

# Вычисление F1-меры
f1 = f1_score(labels, predictions, average='weighted')
print("F1 Score:", f1)

# Вычисление матрицы ошибок
cm = confusion_matrix(labels, predictions)
print("Confusion Matrix:\n", cm)

# Визуализация матрицы ошибок
plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Correct', 'Correct'], yticklabels=['Not Correct', 'Correct'])
plt.ylabel('Actual')
plt.xlabel('Predicted')

plt.title('Confusion Matrix')
plt.show()
