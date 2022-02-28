import create_db.config as db_config
import config
import TokenizedLyricsDataset
from preprocessing import preprocess

import os
import random
from pathlib import Path
import shutil

def copy_then_preprocess_song(from_path, root):
  from_path = str(from_path)
  name = from_path.split(os.path.sep)[-1]
  folder = from_path.split(os.path.sep)[-2]
  folder_path = Path(os.path.join(root, folder))
  to_path = os.path.join(root, folder, name)

  Path.mkdir(folder_path, parents=True, exist_ok=True)
  shutil.copy(from_path, to_path)
  preprocess(to_path)

def create_datasets():
  paths = []
  root = db_config.DB_PATH
  for folder_name in os.listdir(root):
    folder = os.path.join(root, folder_name)
    if os.path.isdir(folder):
      for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
          paths.append(file_path)

  random.Random(666).shuffle(paths)
  split_ind = int(len(paths) * config.TRAIN_TEST_SPLIT)
  train_paths = paths[:split_ind]
  test_paths = paths[split_ind:]

  for path in train_paths:
    copy_then_preprocess_song(path, config.TRAIN_PATH)

  for path in test_paths:
    copy_then_preprocess_song(path, config.TEST_PATH)

  train_dataset = TokenizedLyricsDataset(train_paths, True)
  test_dataset = TokenizedLyricsDataset(test_paths, False)

  return train_dataset, test_dataset

create_datasets()