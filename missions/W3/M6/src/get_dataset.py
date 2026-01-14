from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="McAuley-Lab/Amazon-Reviews-2023",
    repo_type="dataset",
    local_dir="./amazon_reviews_2023",
    local_dir_use_symlinks=False
)