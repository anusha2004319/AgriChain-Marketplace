import matplotlib.pyplot as plt
import numpy as np
models = ['Standalone Prophet', 'Standalone CatBoost', 'Hybrid VotingRegressor']
rmse_scores = [18.4, 14.2, 11.8] 
accuracy_scores = [82.5, 89.4, 94.1] 

x = np.arange(len(models))
width = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
rects1 = ax.bar(x - width/2, accuracy_scores, width, label='Accuracy (%)', color='#2ecc71')
rects2 = ax.bar(x + width/2, rmse_scores, width, label='RMSE (Lower is Better)', color='#e74c3c')
ax.set_ylabel('Scores')
ax.set_title('Performance Comparison of Forecasting Models')
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend()
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)

fig.tight_layout()
plt.savefig('model_comparison_ijert.png', dpi=300) 
plt.show()