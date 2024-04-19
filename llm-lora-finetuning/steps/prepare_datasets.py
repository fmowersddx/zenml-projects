# Apache Software License 2.0
#
# Copyright (c) ZenML GmbH 2024. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from functools import partial
from pathlib import Path

from materializers.directory_materializer import DirectoryMaterializer
from typing_extensions import Annotated
from utils.cuda import cleanup_memory
from utils.tokenizer import generate_and_tokenize_prompt, load_tokenizer
from zenml import log_model_metadata, step
from zenml.materializers import BuiltInMaterializer


@step(output_materializers=[DirectoryMaterializer, BuiltInMaterializer])
def prepare_data(
    base_model_id: str,
    system_prompt: str,
    dataset_name: str = "gem/viggo",
    use_fast: bool = True,
) -> Annotated[Path, "datasets_dir"]:
    """Prepare the datasets for finetuning.

    Args:
        base_model_id: The base model id to use.
        system_prompt: The system prompt to use.
        dataset_name: The name of the dataset to use.
        use_fast: Whether to use the fast tokenizer.

    Returns:
        The path to the datasets directory.
    """
    from datasets import load_dataset

    cleanup_memory()

    log_model_metadata(
        {
            "system_prompt": system_prompt,
            "base_model_id": base_model_id,
        }
    )

    tokenizer = load_tokenizer(base_model_id, False, use_fast)
    gen_and_tokenize = partial(
        generate_and_tokenize_prompt,
        tokenizer=tokenizer,
        system_prompt=system_prompt,
    )

    train_dataset = load_dataset(dataset_name, split="train")
    tokenized_train_dataset = train_dataset.map(gen_and_tokenize)
    eval_dataset = load_dataset(dataset_name, split="validation")
    tokenized_val_dataset = eval_dataset.map(gen_and_tokenize)
    test_dataset = load_dataset(dataset_name, split="test")

    datasets_path = Path("datasets")
    tokenized_train_dataset.save_to_disk(datasets_path / "train")
    tokenized_val_dataset.save_to_disk(datasets_path / "val")
    test_dataset.save_to_disk(datasets_path / "test_raw")

    return datasets_path
