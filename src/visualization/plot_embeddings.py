"""
Biometric embedding visualization module.
Projects 128-dimensional fingerprint representations into 2D manifolds using PCA and t-SNE.
"""

from pathlib import Path
from typing import List, Optional, Any
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


def plot_pca_embeddings(
    embeddings: np.ndarray,
    identities: List[Any],
    output_dir: Path,
    title_suffix: str = "",
):
    """
    Computes PCA 2D projection and plots identity clusters.
    """
    pca = PCA(n_components=2, random_state=42)
    reduced = pca.fit_transform(embeddings)
    var_exp = pca.explained_variance_ratio_

    fig, ax = plt.subplots(figsize=(9, 7))
    palette = sns.color_palette("tab10", n_colors=len(set(identities)))
    sns.scatterplot(
        x=reduced[:, 0],
        y=reduced[:, 1],
        hue=identities,
        palette=palette,
        s=65,
        alpha=0.85,
        edgecolor="w",
        ax=ax,
    )

    ax.set_title(
        f"2D PCA Projection of 128-D Fingerprint Embeddings {title_suffix}\n(Explained Variance: PC1={var_exp[0]*100:.1f}%, PC2={var_exp[1]*100:.1f}%)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Principal Component 1", fontsize=11)
    ax.set_ylabel("Principal Component 2", fontsize=11)
    ax.legend(title="Subject ID", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    out_path = output_dir / f"embedding_pca_visualization{title_suffix.replace(' ', '_').lower()}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_tsne_embeddings(
    embeddings: np.ndarray,
    identities: List[Any],
    output_dir: Path,
    perplexity: float = 15.0,
    title_suffix: str = "",
):
    """
    Computes t-SNE 2D projection and plots identity manifold separation.
    """
    tsne = TSNE(n_components=2, perplexity=min(perplexity, len(embeddings) - 1), random_state=42, max_iter=1000)
    reduced = tsne.fit_transform(embeddings)

    fig, ax = plt.subplots(figsize=(9, 7))
    palette = sns.color_palette("tab10", n_colors=len(set(identities)))
    sns.scatterplot(
        x=reduced[:, 0],
        y=reduced[:, 1],
        hue=identities,
        palette=palette,
        s=65,
        alpha=0.85,
        edgecolor="w",
        ax=ax,
    )

    ax.set_title(
        f"2D t-SNE Manifold Clustering of Biometric Fingerprint Embeddings {title_suffix}",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("t-SNE Dimension 1", fontsize=11)
    ax.set_ylabel("t-SNE Dimension 2", fontsize=11)
    ax.legend(title="Subject ID", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    out_path = output_dir / f"embedding_tsne_visualization{title_suffix.replace(' ', '_').lower()}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")
