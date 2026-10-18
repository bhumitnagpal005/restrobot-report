import styles from './RestaurantModal.module.css'

const RESTAURANTS = [
  {
    name: 'Limra Garden Restaurant',
    cuisines: 'Chinese, Rolls, Fast Food, Beef & Chicken Specials',
    location: 'Kosapet, Vellore',
    sample: 'What fast food and roll options are available at Limra Garden Restaurant in Kosapet?',
    icon: '🥘',
  },
  {
    name: 'KFC',
    cuisines: 'American Fast Food, Fried Chicken, Burgers, Rice Bowls',
    location: 'Katpadi, Vellore',
    sample: 'What is the price of chicken Zinger burger and rice boxes at KFC in Katpadi?',
    icon: '🍗',
  },
  {
    name: "Domino's Pizza",
    cuisines: 'Pizza, Pasta, Garlic Bread, Desserts',
    location: 'Gandhi Nagar, Vellore',
    sample: "List pizza combos and side dishes at Domino's in Gandhi Nagar, Vellore.",
    icon: '🍕',
  },
  {
    name: 'Pizza Hut',
    cuisines: 'Italian, Pizza, Pastas, Appetizers',
    location: 'Gandhi Nagar, Vellore',
    sample: 'What vegetarian pizza options are available at Pizza Hut in Gandhi Nagar?',
    icon: '🍕',
  },
  {
    name: 'Frozen Bottle',
    cuisines: 'Thick Milkshakes, Sundaes, Jar Cakes, Ice Cream',
    location: 'Katpadi, Vellore',
    sample: 'What thick milkshakes and ice cream sundaes are available at Frozen Bottle in Katpadi?',
    icon: '🥤',
  },
  {
    name: 'Kailash Parbat',
    cuisines: 'Pure Veg, North & South Indian, Chaat, Chinese',
    location: 'Sathuvachari, Vellore',
    sample: 'Show me pure veg chaat and South Indian items at Kailash Parbat in Sathuvachari.',
    icon: '🥗',
  },
  {
    name: 'Saleem Punjabi Dhaba',
    cuisines: 'North Indian, Punjabi Dhaba Specials, Tandoori & Gravies',
    location: 'Katpadi, Vellore',
    sample: 'What Punjabi chicken and naan options are served at Saleem Punjabi Dhaba in Katpadi?',
    icon: '🍲',
  },
  {
    name: "Uncle Peter's Pancakes",
    cuisines: 'Pancakes, Waffles, Crepes, Desserts, Cafe',
    location: 'Katpadi, Vellore',
    sample: "What sweet pancakes and waffles are available at Uncle Peter's Pancakes in Katpadi?",
    icon: '🥞',
  },
  {
    name: 'Wow! Momo',
    cuisines: 'Steamed & Fried Momos, Momo Burgers, Beverages',
    location: 'Katpadi, Vellore',
    sample: 'What chicken and veg momo varieties are offered at Wow! Momo in Katpadi?',
    icon: '🥟',
  },
  {
    name: 'Zorko - Brand of Food Lovers',
    cuisines: 'Burgers, Pizzas, Sandwiches, Shakes, Fast Food',
    location: 'Katpadi, Vellore',
    sample: 'What fast food burgers and sandwiches are available at Zorko Katpadi?',
    icon: '🍔',
  },
  {
    name: 'Lassi House',
    cuisines: 'Lassis, Beverages, Juices, Ice Creams, Snacks',
    location: 'Katpadi, Vellore',
    sample: 'What lassi flavors and cold beverages are available at Lassi House Katpadi?',
    icon: '🥛',
  },
  {
    name: 'Pastel Poetry',
    cuisines: 'Bakery, Desserts, Cafe, Continental',
    location: 'Gandhi Nagar, Vellore',
    sample: 'What cafe items and desserts are served at Pastel Poetry in Gandhi Nagar?',
    icon: '🍰',
  },
  {
    name: 'Hundreds Heritage',
    cuisines: 'North Indian, Chinese, Continental Multi-cuisine',
    location: 'Gandhi Nagar, Vellore',
    sample: 'What multi-cuisine dishes are offered at Hundreds Heritage in Gandhi Nagar?',
    icon: '🏛️',
  },
]

export default function RestaurantModal({ onClose, onSelectSample }) {
  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <div>
            <h2 className={styles.title}>Vellore Restaurants ({RESTAURANTS.length}) 📍</h2>
            <p className={styles.subtitle}>Explore available menus loaded from runner.py & Zomato Vellore</p>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>&times;</button>
        </div>

        <div className={styles.grid}>
          {RESTAURANTS.map((resto, idx) => (
            <div key={idx} className={styles.card}>
              <div className={styles.cardHeader}>
                <span className={styles.icon}>{resto.icon}</span>
                <div>
                  <h3 className={styles.restoName}>{resto.name}</h3>
                  <span className={styles.location}>📍 {resto.location}</span>
                </div>
              </div>
              <p className={styles.cuisines}>{resto.cuisines}</p>
              <button
                className={styles.askBtn}
                onClick={() => onSelectSample(resto.sample)}
              >
                Ask about menu &rarr;
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
