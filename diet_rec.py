# -*- coding: utf-8 -*-
"""Diet Rec

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15UonxCzInyrEb1LKkOVVNER1prF8EQHb
"""



import numpy as np
import pandas as pd
import skfuzzy as fuzz
import skfuzzy.control as ctrl



file_path = "diet_recommendations_dataset.csv"
df = pd.read_csv(file_path)


#drop unnecessary cols
df = df.drop(['Patient_ID','Weight_kg', 'Height_cm', 'Preferred_Cuisine', 'Allergies', 'Dietary_Nutrient_Imbalance_Score'], axis=1)


# @title Age

from matplotlib import pyplot as plt
df['Age'].plot(kind='hist', bins=20, title='Age')
plt.gca().spines[['top', 'right',]].set_visible(False)

#plot chart for target class Weekly_Exercise_Hours
df['Weekly_Exercise_Hours'].plot(kind='hist', bins=20, title='Weekly Exercise Hours')
plt.gca().spines[['top', 'right',]].set_visible(False)

#plot chart for target class Diet_Recommendation
df['Diet_Recommendation'].value_counts().plot(kind='bar', title='Diet Recommendation')
plt.gca().spines[['top', 'right',]].set_visible(False)





#load Anuvaad_INDB_2024.11.xlsx into df
food_df = pd.read_excel('Anuvaad_INDB_2024.11.xlsx')




food_df = food_df.drop(['food_code','primarysource'], axis=1)


file_path = "collected_data.csv"
collected_df = pd.read_csv(file_path)
collected_df = collected_df.drop(collected_df.columns[0], axis=1)
collected_df.columns = ['Gender', 'Age','Weight', 'Height', 'State', 'Activity', 'SleepQuality','MealIntake', 'WaterIntake', 'CheatMeals', 'HealthyMeals', 'Disease', 'DietaryRestrictions']

def classify_diet(row):
    classes = []

    # Calculate net carbs and energy ratios
    net_carbs = row['carb_g'] - row['fibre_g']
    protein_ratio = (row['protein_g'] * 4) / row['energy_kcal'] if row['energy_kcal'] > 0 else 0
    fat_density = (row['fat_g'] / (row['energy_kcal'] / 100)) if row['energy_kcal'] > 0 else 999


    if net_carbs < 20:  
        classes.append('Low_Carb')

    if row['sodium_mg'] < 140:  
        classes.append('Low_Sodium')

    if row['protein_g'] > 8 and protein_ratio > 0.15:  
        classes.append('High_Protein')

    if fat_density < 5:  
        classes.append('Low_Fat')

    if row['fibre_g'] > 2: 
        classes.append('High_Fiber')

    if row['freesugar_g'] < 7:  
        classes.append('Low_Sugar')

    balanced_criteria = {'Low_Sodium', 'Low_Fat', 'High_Fiber', 'High_Protein', 'Low_Sugar'}
    if len(set(classes) & balanced_criteria) >= 3:
        classes.append('Balanced')

    return classes


def health_condition_classification(row):
    classes = []

    # Convert mg to g for fatty acids
    sfa_g = row['sfa_mg'] / 1000
    mufa_g = row['mufa_mg'] / 1000
    pufa_g = row['pufa_mg'] / 1000

    # Diabetes-Friendly Criteria (ADA guidelines)
    net_carbs = row['carb_g'] - row['fibre_g']
    if (net_carbs < 30 and
        row['freesugar_g'] < 8 and
        row['fibre_g'] > 5 and
        (mufa_g + pufa_g) > sfa_g):  # More unsaturated fats
        classes.append('Diabetes-Friendly')

    # Heart-Healthy Criteria (AHA guidelines)
    if (row['sodium_mg'] < 400 and
        sfa_g < 3 and
        row['cholesterol_mg'] < 200 and  # Less strict threshold
        (mufa_g + pufa_g) > sfa_g):
        classes.append('Heart-Healthy')

    # Weight Management Criteria
    # Use unit_serving_energy_kcal for calorie density (per serving)
    if (row['unit_serving_energy_kcal'] < 300 and  # Moderate calorie limit
        row['protein_g'] > 7 and                   # Moderate protein
        row['fibre_g'] > 2):                       # Some fiber
        classes.append('Weight_Management')

    # Renal-Friendly Criteria (low protein, sodium, potassium, phosphorus)
    if (row['protein_g'] < 10 and
        row['sodium_mg'] < 200 and
        row['potassium_mg'] < 200 and
        row['phosphorus_mg'] < 100):
        classes.append('Renal-Friendly')

    return classes

food_df['diet_classes'] = food_df.apply(classify_diet, axis=1)
food_df['health_condition_classes'] = food_df.apply(health_condition_classification, axis=1)
#display food name and last two cols, print any random 10
food_df[['food_name', 'diet_classes', 'health_condition_classes']].sample(10)

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# First apply classifications to your dataframe
food_df['Diet_Class'] = food_df.apply(classify_diet, axis=1)
food_df['Health_Condition'] = food_df.apply(health_condition_classification, axis=1)

# Create binary columns for each health condition
conditions = ['Diabetes-Friendly', 'Heart-Healthy', 'Weight_Management', 'Renal-Friendly']
for cond in conditions:
    food_df[cond] = food_df['Health_Condition'].apply(lambda x: 1 if cond in x else 0)

# Select relevant nutrient columns
nutrient_cols = [
    'carb_g', 'fibre_g', 'freesugar_g', 'protein_g', 'fat_g',
    'sfa_mg', 'mufa_mg', 'pufa_mg', 'cholesterol_mg',
    'sodium_mg', 'potassium_mg', 'phosphorus_mg',
    'energy_kcal', 'unit_serving_energy_kcal'
]

# Calculate correlations
corr_matrix = food_df[nutrient_cols + conditions].corr()

# Plot heatmap for health conditions
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix.loc[conditions, nutrient_cols],
            annot=True, cmap='coolwarm', center=0,
            vmin=-1, vmax=1, fmt='.2f')
plt.title('Correlation Between Nutrients and Health Conditions')
plt.tight_layout()
plt.show()

food_df['Diet_Class'].explode().value_counts().plot(
    kind='bar',
    color=['#4CAF50', '#2196F3', '#FFC107', '#F44336']
)
plt.title('Frequency of Diet Classes')
plt.ylabel('Count')
plt.show()

#show df.head() with all cols
pd.set_option('display.max_columns', None)
food_df.head()


def create_fuzzy_systems():
    # Input variables
    bmi = ctrl.Antecedent(np.arange(10, 50, 0.1), 'bmi')
    glucose = ctrl.Antecedent(np.arange(70, 250, 1), 'glucose')
    cholesterol = ctrl.Antecedent(np.arange(100, 300, 1), 'cholesterol')
    blood_pressure = ctrl.Antecedent(np.arange(80, 200, 1), 'blood_pressure')
    activity = ctrl.Antecedent(np.arange(0, 15, 0.1), 'activity')
    age = ctrl.Antecedent(np.arange(18, 100, 1), 'age')

    # Define membership functions for inputs (same as before)
    # BMI
    bmi['underweight'] = fuzz.trimf(bmi.universe, [10, 15, 18.5])
    bmi['normal'] = fuzz.trimf(bmi.universe, [17, 22, 25])
    bmi['overweight'] = fuzz.trimf(bmi.universe, [25, 27.5, 30])
    bmi['obese'] = fuzz.trimf(bmi.universe, [28, 35, 42])
    bmi['severely_obese'] = fuzz.trimf(bmi.universe, [40, 45, 50])

    # Glucose
    glucose['normal'] = fuzz.trimf(glucose.universe, [70, 90, 120])
    glucose['prediabetic'] = fuzz.trimf(glucose.universe, [100, 125, 150])
    glucose['diabetic'] = fuzz.trimf(glucose.universe, [130, 180, 250])

    # Cholesterol
    cholesterol['normal'] = fuzz.trimf(cholesterol.universe, [100, 150, 220])
    cholesterol['borderline'] = fuzz.trimf(cholesterol.universe, [190, 225, 260])
    cholesterol['high'] = fuzz.trimf(cholesterol.universe, [240, 275, 300])

    # Blood pressure
    blood_pressure['normal'] = fuzz.trimf(blood_pressure.universe, [80, 100, 130])
    blood_pressure['elevated'] = fuzz.trimf(blood_pressure.universe, [120, 130, 150])
    blood_pressure['high'] = fuzz.trimf(blood_pressure.universe, [140, 160, 190])
    blood_pressure['crisis'] = fuzz.trimf(blood_pressure.universe, [170, 190, 200])

    # Activity
    activity['sedentary'] = fuzz.trimf(activity.universe, [0, 2, 6])
    activity['moderate'] = fuzz.trimf(activity.universe, [4, 7, 11])
    activity['active'] = fuzz.trimf(activity.universe, [9, 12, 15])

    # Age
    age['young'] = fuzz.trimf(age.universe, [18, 25, 40])
    age['middle'] = fuzz.trimf(age.universe, [35, 50, 70])
    age['senior'] = fuzz.trimf(age.universe, [60, 75, 100])

    # Create separate output variables for each diet class
    low_carb = ctrl.Consequent(np.arange(0, 100, 1), 'low_carb')
    low_sodium = ctrl.Consequent(np.arange(0, 100, 1), 'low_sodium')
    high_protein = ctrl.Consequent(np.arange(0, 100, 1), 'high_protein')
    low_fat = ctrl.Consequent(np.arange(0, 100, 1), 'low_fat')
    high_fiber = ctrl.Consequent(np.arange(0, 100, 1), 'high_fiber')
    low_sugar = ctrl.Consequent(np.arange(0, 100, 1), 'low_sugar')
    balanced = ctrl.Consequent(np.arange(0, 100, 1), 'balanced')
    diabetes_friendly = ctrl.Consequent(np.arange(0, 100, 1), 'diabetes_friendly')
    heart_healthy = ctrl.Consequent(np.arange(0, 100, 1), 'heart_healthy')
    weight_management = ctrl.Consequent(np.arange(0, 100, 1), 'weight_management')

    # Define simple membership functions for outputs
    for output in [low_carb, low_sodium, high_protein, low_fat, high_fiber, 
                   low_sugar, balanced, diabetes_friendly, heart_healthy, weight_management]:
        output['not_recommended'] = fuzz.trimf(output.universe, [0, 0, 50])
        output['recommended'] = fuzz.trimf(output.universe, [50, 100, 100])

    # Define rules for each diet class
    low_carb_rules = [
        ctrl.Rule(glucose['prediabetic'] & bmi['overweight'], low_carb['recommended']),
        ctrl.Rule(glucose['prediabetic'] & bmi['obese'], low_carb['recommended']),
        ctrl.Rule(glucose['diabetic'], low_carb['recommended'])
    ]
    
    low_sodium_rules = [
        ctrl.Rule(blood_pressure['elevated'] | blood_pressure['high'], low_sodium['recommended']),
        ctrl.Rule(blood_pressure['crisis'], low_sodium['recommended'])
    ]
    
    high_protein_rules = [
        ctrl.Rule(activity['active'] & (bmi['underweight'] | bmi['normal']), high_protein['recommended']),
        ctrl.Rule(activity['moderate'] & age['young'], high_protein['recommended'])
    ]
    
    low_fat_rules = [
        ctrl.Rule(cholesterol['high'] & ~glucose['diabetic'], low_fat['recommended']),
        ctrl.Rule(bmi['overweight'] & glucose['normal'] & blood_pressure['normal'], low_fat['recommended']),
        ctrl.Rule(activity['sedentary'] & (bmi['normal'] | bmi['overweight']), low_fat['recommended'])
    ]
    
    high_fiber_rules = [
        ctrl.Rule(age['senior'] & ~(glucose['diabetic'] | cholesterol['high']), high_fiber['recommended'])
    ]
    
    low_sugar_rules = [
        ctrl.Rule((glucose['prediabetic'] | glucose['diabetic']) & ~bmi['underweight'], low_sugar['recommended'])
    ]
    
    balanced_rules = [
        ctrl.Rule(bmi['normal'] & glucose['normal'] & blood_pressure['normal'] & cholesterol['normal'], balanced['recommended']),
        ctrl.Rule(age['middle'] & bmi['normal'], balanced['recommended'])
    ]
    
    diabetes_friendly_rules = [
        ctrl.Rule(glucose['diabetic'], diabetes_friendly['recommended'])
    ]
    
    heart_healthy_rules = [
        ctrl.Rule((blood_pressure['high'] | blood_pressure['crisis']) & cholesterol['high'], heart_healthy['recommended'])
    ]
    
    weight_management_rules = [
        ctrl.Rule(bmi['obese'] | bmi['severely_obese'], weight_management['recommended']),
        ctrl.Rule(bmi['overweight'], weight_management['recommended'])
    ]

    low_fat_rules.extend([
    ctrl.Rule(cholesterol['borderline'], low_fat['recommended']),
    ctrl.Rule(cholesterol['high'], low_fat['recommended'])
    ])

    high_fiber_rules.extend([
        ctrl.Rule(cholesterol['borderline'] | cholesterol['high'], high_fiber['recommended'])
    ])

    heart_healthy_rules.extend([
        ctrl.Rule(cholesterol['high'], heart_healthy['recommended']),
        ctrl.Rule(cholesterol['borderline'] & age['middle'], heart_healthy['recommended']),
        ctrl.Rule(cholesterol['borderline'] & age['senior'], heart_healthy['recommended'])
    ])


    # Create control systems for each diet class
    systems = {}
    systems['Low_Carb'] = ctrl.ControlSystem(low_carb_rules)
    systems['Low_Sodium'] = ctrl.ControlSystem(low_sodium_rules)
    systems['High_Protein'] = ctrl.ControlSystem(high_protein_rules)
    systems['Low_Fat'] = ctrl.ControlSystem(low_fat_rules)
    systems['High_Fiber'] = ctrl.ControlSystem(high_fiber_rules)
    systems['Low_Sugar'] = ctrl.ControlSystem(low_sugar_rules)
    systems['Balanced'] = ctrl.ControlSystem(balanced_rules)
    systems['Diabetes_Friendly'] = ctrl.ControlSystem(diabetes_friendly_rules)
    systems['Heart_Healthy'] = ctrl.ControlSystem(heart_healthy_rules)
    systems['Weight_Management'] = ctrl.ControlSystem(weight_management_rules)
    
    return systems

def get_diet_recommendations(row, fuzzy_systems):
    recommendations = []
    recommendation_scores = {}
    
    for diet_class, system in fuzzy_systems.items():
        try:
            sim = ctrl.ControlSystemSimulation(system)
            
            # Set inputs
            sim.input['bmi'] = row['BMI']
            sim.input['glucose'] = row['Glucose_mg/dL']
            sim.input['cholesterol'] = row['Cholesterol_mg/dL']
            sim.input['blood_pressure'] = row['Blood_Pressure_mmHg']
            sim.input['activity'] = row['Weekly_Exercise_Hours']
            sim.input['age'] = row['Age']
            
            # Compute
            sim.compute()
            
            # Get output name (lowercase version of diet_class)
            output_name = diet_class.lower().replace('_', '')
            
            # Store recommendation score
            score = sim.output[output_name]
            recommendation_scores[diet_class] = score
            
            # If recommendation score is high enough, add to recommendations
            if score > 50:  # Threshold for recommendation
                recommendations.append(diet_class)
        except:
            # Skip if this particular system fails
            continue
    
    # If no recommendations were made, use fallback
    if not recommendations:
        recommendations = [rule_based_diet_recommendation(row)]
    
    return recommendations, recommendation_scores

# Rule-based diet recommendation as fallback
def rule_based_diet_recommendation(row):
    if row['Disease_Type'] == 'Diabetes':
        return 'Low_Carb'
    elif row['Disease_Type'] == 'Hypertension':
        return 'Low_Sodium'
    elif row['Weekly_Exercise_Hours'] > 8:
        return 'High_Protein'
    else:
        return 'Balanced'

# Function to get additional health-specific diet classes
def get_health_specific_classes(row):
    classes = []

    if row['Disease_Type'] == 'Diabetes' or row['Glucose_mg/dL'] > 130:
        classes.append('Diabetes-Friendly')

    if row['Disease_Type'] == 'Hypertension' or row['Blood_Pressure_mmHg'] > 140:
        classes.append('Heart-Healthy')

    if row['BMI'] >= 27 or row['Disease_Type'] == 'Obesity' :
        classes.append('Weight_Management')

    if row['Dietary_Restrictions'] == 'Low_Sodium':
        classes.append('Renal-Friendly')

    if row['Dietary_Restrictions'] == 'Low_Sugar':
        classes.append('Low_Sugar')

    return classes

def apply_new_diet_classification(df):
    # Create fuzzy systems
    fuzzy_systems = create_fuzzy_systems()
    
    # Apply fuzzy logic to get diet recommendations
    results = df.apply(lambda row: get_diet_recommendations(row, fuzzy_systems), axis=1)
    
    # Extract recommendations and scores
    df['Diet_Recommendations'] = results.apply(lambda x: x[0])
    df['Recommendation_Scores'] = results.apply(lambda x: x[1])
    
    # Get primary recommendation (highest score)
    df['Primary_Diet_Recommendation'] = df.apply(
        lambda row: max(row['Recommendation_Scores'].items(), key=lambda x: x[1])[0] 
        if row['Recommendation_Scores'] else rule_based_diet_recommendation(row),
        axis=1
    )
    
    # Apply additional health-specific restrictions
    df['Additional_Diet_Classes'] = df.apply(get_health_specific_classes, axis=1)
    
    # Clean up None values
    df['Additional_Diet_Classes'] = df['Additional_Diet_Classes'].apply(lambda x: [item for item in x if item is not None])
    
    # Combine all recommendations
    df['Complete_Diet_Classes'] = df.apply(
        lambda row: row['Diet_Recommendations'] + row['Additional_Diet_Classes'],
        axis=1
    )
    
    return df

# Apply the classification
df = apply_new_diet_classification(df)


# df = df.drop(['New_Diet_Recommendation', 'Additional_Diet_Classes'], axis=1)



import pandas as pd

def match_foods_to_users(df, food_df):
    user_food_recommendations = []

    for user_classes in df['Complete_Diet_Classes']:
        # Filter foods that match ALL of the user's classes
        matching_foods = food_df[food_df['diet_classes'].apply(lambda x: all(cls in x for cls in user_classes))]

        # If no exact match, find foods that match at least the health condition class
        if matching_foods.empty:
            matching_foods = food_df[food_df['health_condition_classes'].apply(lambda x: any(cls in x for cls in user_classes))]

        user_food_recommendations.append(matching_foods['food_name'].tolist())

    return user_food_recommendations

def display_food_weights(recommender):
    st.subheader("Food Weights")
    total_foods = len(recommender.food_weights)
    st.write(f"Total number of foods: {total_foods}")
    
    # Sort foods by weight in descending order
    sorted_foods = sorted(recommender.food_weights.items(), key=lambda x: x[1], reverse=True)
    
    # Display top 10 foods with highest weights
    st.write("Top 10 foods by weight:")
    for food, weight in sorted_foods[:10]:
        st.write(f"{food}: {weight:.2f}")

import pandas as pd
import numpy as np

class FoodRecommendationRL:
    def __init__(self, food_df):
        self.food_df = food_df
        self.user_preferences = {}
        self.food_weights = {}
        self.learning_rate = 0.1

    def match_foods_to_user(self, user_classes):
        # Filter foods that match ALL of the user's classes
        matching_foods = self.food_df[self.food_df['diet_classes'].apply(lambda x: all(cls in x for cls in user_classes))]

        # If no exact match, find foods that match at least the health condition class
        if matching_foods.empty:
            matching_foods = self.food_df[self.food_df['health_condition_classes'].apply(lambda x: any(cls in x for cls in user_classes))]

        return matching_foods['food_name'].tolist()

    def get_initial_recommendations(self, user_id, user_classes):
        recommended_foods = self.match_foods_to_user(user_classes)

        for food in recommended_foods:
            if food not in self.food_weights:
                self.food_weights[food] = 1.0

        return recommended_foods

    def get_weighted_recommendations(self, user_id, recommended_foods, top_n=100):
        weighted_foods = [(food, self.food_weights.get(food, 1.0))
                          for food in recommended_foods]
        weighted_foods.sort(key=lambda x: x[1], reverse=True)
        return [food for food, _ in weighted_foods[:top_n]]

    def update_weights(self, user_id, food, liked):
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}

        self.user_preferences[user_id][food] = liked

        current_weight = self.food_weights.get(food, 1.0)
        if liked:
            new_weight = current_weight + self.learning_rate
        else:
            new_weight = current_weight - (self.learning_rate*3)

        self.food_weights[food] = max(0.1, min(new_weight, 2.0))

    def get_recommendations(self, user_id, user_classes, top_n=100):
        initial_recs = self.get_initial_recommendations(user_id, user_classes)

        if user_id in self.user_preferences and self.user_preferences[user_id]:
            weighted_recs = self.get_weighted_recommendations(user_id, initial_recs, top_n)
            return weighted_recs

        return initial_recs[:top_n]

# Example of how to use with your fuzzy logic system:

# Initialize the recommender with session state
recommender = FoodRecommendationRL(food_df)

# Get recommendations for a user based on their fuzzy-derived classes
def get_personalized_recommendations(row):
    user_id = row.name  # Using DataFrame index as user_id
    user_classes = row['Complete_Diet_Classes']  # From your fuzzy logic system
    return recommender.get_recommendations(user_id, user_classes)

# Apply to get initial recommendations
df['Recommended_Foods'] = df.apply(get_personalized_recommendations, axis=1)

# Example of simulating user feedback
# For user with index 0
user_id = 0
if len(df.loc[user_id, 'Recommended_Foods']) > 0:
    # User likes the first food
    recommender.update_weights(user_id, df.loc[user_id, 'Recommended_Foods'][0], liked=True)

    # User dislikes the second food (if available)
    if len(df.loc[user_id, 'Recommended_Foods']) > 1:
        recommender.update_weights(user_id, df.loc[user_id, 'Recommended_Foods'][1], liked=False)

# Update recommendations after feedback
df['Updated_Recommendations'] = df.apply(get_personalized_recommendations, axis=1)

# View the results
# Function to apply fuzzy logic and get diet classes
def get_diet_classes(user_data):
    user_df = pd.DataFrame([user_data])
    user_df = apply_new_diet_classification(user_df)
    return user_df.loc[0, 'Complete_Diet_Classes']

import streamlit as st

# Initialize session state variables
if 'current_recommendations' not in st.session_state:
    st.session_state.current_recommendations = []
if 'feedback_given' not in st.session_state:
    st.session_state.feedback_given = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = "new_user"
if 'food_weights' not in st.session_state:
    st.session_state.food_weights = {}
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {}

recommender.food_weights = st.session_state.food_weights
recommender.user_preferences = st.session_state.user_preferences


# Streamlit app
def main():
    st.title("Diet Recommendation System")
    st.sidebar.header("User Information")

    with st.sidebar.form(key='user_inputs'):
        age = st.number_input("Age", min_value=18, max_value=100, value=23, step=1)
        bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=22.5, step=0.1)
        glucose = st.number_input("Glucose (mg/dL)", min_value=50, max_value=300, value=100, step=1)
        cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=100, max_value=300, value=200, step=1)
        blood_pressure = st.number_input("Blood Pressure (mmHg)", min_value=80, max_value=200, value=120, step=1)
        exercise_hours = st.number_input("Weekly Exercise Hours", min_value=0, max_value=20, value=3, step=1)
        disease_type = st.selectbox("Disease Type", ["None", "Diabetes", "Hypertension", "Obesity"])
        dietary_restrictions = st.selectbox("Dietary Restrictions", ["None", "Low_Sodium", "Low_Sugar"])
        
        submit_button = st.form_submit_button(label='Generate Classes')\
    # Create user data dictionary
    user_data = {
        'Age': age,
        'BMI': bmi,
        'Glucose_mg/dL': glucose,
        'Cholesterol_mg/dL': cholesterol,
        'Blood_Pressure_mmHg': blood_pressure,
        'Weekly_Exercise_Hours': exercise_hours,
        'Disease_Type': disease_type,
        'Dietary_Restrictions': dietary_restrictions
    }

    # Compute diet classes using fuzzy logic
    diet_classes = get_diet_classes(user_data)
    st.write(f"Recommended Diet Classes: {diet_classes}")

    # Get initial recommendations if none exist or if user clicks "Get New Recommendations"
    import random

    if len(st.session_state.current_recommendations) == 0 or st.button("Get New Recommendations"):
        recommender.food_weights = st.session_state.food_weights
        recommender.user_preferences = st.session_state.user_preferences
        
        recommendations = recommender.get_recommendations(st.session_state.user_id, diet_classes)
        random.shuffle(recommendations)  # Shuffle the recommendations
        
        st.session_state.current_recommendations = recommendations
        st.session_state.feedback_given = False



    # Display current recommendations
    st.subheader("Food Recommendations")
    if st.session_state.current_recommendations:
        with st.form(key="feedback_form"):
            for i, food in enumerate(st.session_state.current_recommendations[:10], 1):
                st.write(f"{i}. {food}")
                
                # Use a radio button for Yes/No/Neutral feedback
                feedback = st.radio(
                    f"Did you like {food}?", 
                    options=["Neutral", "Yes", "No"], 
                    key=f"{food}_feedback_{st.session_state.feedback_given}"
                )
                
                # Store feedback in session state
                st.session_state[f"feedback_{food}"] = feedback
            
            # Submit button for the form
            submit_button = st.form_submit_button(label="Update Recommendations")
        
        # Process feedback only after form submission
        if submit_button:
            for food in st.session_state.current_recommendations[:10]:
                feedback = st.session_state.get(f"feedback_{food}")
                if feedback == "Yes":
                    recommender.update_weights(st.session_state.user_id, food, liked=True)
                elif feedback == "No":
                    recommender.update_weights(st.session_state.user_id, food, liked=False)

            st.session_state.food_weights = recommender.food_weights
            st.session_state.user_preferences = recommender.user_preferences

            # Get updated recommendations after processing all feedback
            st.session_state.current_recommendations = recommender.get_recommendations(st.session_state.user_id, diet_classes)
            st.session_state.feedback_given = not st.session_state.feedback_given
            st.rerun()
    else:
        st.write("No recommendations available for the given diet classes.")


if __name__ == "__main__":
    main()
